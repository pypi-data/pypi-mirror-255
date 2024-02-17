#************************************************************************
# Copyright 2023 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************
"""Module allows to view and access Security Hub resources"""


#--------------------------------
#
#--------------------------------
import logging
import datetime
import pprint
import pandas as pd

import botocore.errorfactory


from o7util.table import TableParam, ColumnParam, Table
import o7util.menu as o7m
import o7util.terminal as o7t
import o7util.input as o7i
import o7util.html_report as o7hr


import o7lib.aws.base

import o7cli.sts
import o7cli.organizations as o7org

logger=logging.getLogger(__name__)


#*************************************************
#
#*************************************************
class SecurityHub(o7lib.aws.base.Base):
    """Class for SecurityHub """

    FINDINGS_PAGE_SIZE = 40

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/securityhub.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = self.session.client('securityhub')



        self.df_standards : pd.DataFrame = None
        self.df_standards_results : pd.DataFrame = None
        self.df_controls : pd.DataFrame = None
        self.df_controls_results : pd.DataFrame = None
        self.df_findings : pd.DataFrame = None

        self.df_accounts : pd.DataFrame = None

        self.standard : pd.Series = None
        self.control : pd.Series = None
        self.finding : pd.Series = None
        self.account : pd.Series = None
        self.df_menu_findings : pd.DataFrame = None
        self.findings_per_account : pd.DataFrame = None

        self.finding_menu_index : int = 0

        # self.description : dict = None
        # self.enabled_services : list = []
        # self.accounts : list = []
        # self.policies : list = None

    #*************************************************
    #
    #*************************************************
    def load_accounts(self):
        """Load all accounts if we are allowed"""

        logger.info('load_accounts')

        try:
            self.df_accounts = pd.DataFrame(o7org.Organizations(session=self.session).load_accounts().accounts)
            logger.info(f'load_standards: Number of accounts found {len(self.df_accounts.index)}')

        except botocore.exceptions.ClientError:

            logger.info('Not allowed to list accounts for organization')
            self.df_accounts = pd.DataFrame([{
                'Id' : self.session.client('sts').get_caller_identity().get('Account'),
                'Name' : 'Current Account'
            }])

        self.df_accounts.set_index('Id', inplace=True)

        return self


    #*************************************************
    #
    #*************************************************
    def load_standards(self):
        """Load all standards"""

        logger.info('load_standards')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/securityhub/client/describe_standards.html
        paginator = self.client.get_paginator('describe_standards')

        standards = []

        for page in paginator.paginate():
            standards.extend(page.get('Standards', []))


        self.df_standards = pd.DataFrame(standards)
        self.df_standards['Standards'] = self.df_standards['StandardsArn'].str.split(':').str[-1]
        self.df_standards.set_index('Standards', inplace=True)

        self.df_standards['Short'] = self.df_standards['Name'].str.split(' ').str[0] + ' ' + self.df_standards['Name'].str.split(' ').str[-1]

        logger.info(f'load_standards: Number of standards found {len(standards)}')

        self.load_accounts()

        return self

    #*************************************************
    #
    #*************************************************
    def load_enabled_standards(self):
        """Load enabled standards"""

        if self.df_standards is None:
            self.load_standards()

        logger.info('load_enabled_standards')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/securityhub/client/get_enabled_standards.html
        paginator = self.client.get_paginator('get_enabled_standards')
        standards = []

        for page in paginator.paginate():
            standards.extend(page.get('StandardsSubscriptions', []))

        # self.df_standards = pd.DataFrame(standards)
        logger.info(f'load_enabled_standards: Number of standards found {len(standards)}')

        df = pd.DataFrame(standards)
        df['Standards'] = df['StandardsArn'].str.split(':').str[-1]
        df.set_index('Standards', inplace=True)

        self.df_standards = self.df_standards.join(df[['StandardsSubscriptionArn','StandardsStatus']], how='left')

        return self

    #*************************************************
    #
    #*************************************************
    def load_standard_controls(self):
        """Load all controles for each standards"""

        if self.df_standards is None:
            self.load_enabled_standards()

        df_ready = self.df_standards[self.df_standards['StandardsStatus'] == 'READY']

        self.df_controls = None

        for standards, row in df_ready.iterrows():

            controls = []

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/securityhub/client/describe_standards_controls.html
            paginator = self.client.get_paginator('describe_standards_controls')

            for page in paginator.paginate(StandardsSubscriptionArn=row['StandardsSubscriptionArn']):
                controls.extend(page.get('Controls', []))

            df_controls = pd.DataFrame(controls)
            df_controls['Standards'] = standards

            if self.df_controls is None:
                self.df_controls = df_controls
            else:
                self.df_controls = pd.concat([self.df_controls, df_controls], ignore_index=True)

        self.df_controls['ControlStatusUpdatedAt'] = self.df_controls['ControlStatusUpdatedAt'].dt.tz_localize(None)
        self.df_controls['StandardsControl'] = self.df_controls['StandardsControlArn'].str.split(':').str[-1]
        self.df_controls['IsDisabled'] = self.df_controls['ControlStatus'] == 'DISABLED'

        gb = self.df_controls.groupby(['Standards'])
        self.df_standards['ControlsCount'] = gb['ControlId'].count()
        self.df_standards['ControlsDisabled'] = gb['IsDisabled'].sum()



    #*************************************************
    #
    #*************************************************
    def load_findings(self, standard_arn : str = None):
        """Load findings"""

        logger.info(f'load_findings standard_arn={standard_arn}')


        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/securityhub/client/get_findings.html
        paginator = self.client.get_paginator('get_findings')

        findings = []
        filters = {
            'RecordState' : [{
                'Comparison': 'EQUALS',
                'Value': 'ACTIVE'

            }]
        }
        if standard_arn is not None:
            filters['ComplianceStandardsArn'] = [{
                'Comparison': 'EQUALS',
                'Value': standard_arn.split(':')[-1]
            }]

        for page in paginator.paginate(Filters = filters, MaxResults=100):
            txt = str(len(findings)) if len(findings) % 1000 == 0 else '.'
            print(txt, end='', flush=True)
            findings.extend(page.get('Findings', []))
        print(' All finding loaded')


        df = pd.DataFrame(findings)

        df['StandardsArn'] = df['ProductFields'].apply(lambda x: x.get('StandardsArn', x.get('StandardsGuideArn',None)))
        df['ControlId'] = df['ProductFields'].apply(lambda x: x.get('ControlId', x.get('RuleId',None)))
        df['StandardsControlArn'] = df['ProductFields'].apply(lambda x: x.get('StandardsControlArn', None))

        df['Status'] = df['Compliance'].apply(lambda x: x.get('Status', None) if isinstance(x,dict) else x)
        df['WorkflowStatus'] = df['Workflow'].apply(lambda x: x.get('Status', None) if isinstance(x,dict) else x)
        df['passed'] = (df['Status'] == 'PASSED')  | (df['WorkflowStatus'] == 'SUPPRESSED')


        df['SecurityControlId'] = df['Compliance'].apply(lambda x: x.get('SecurityControlId', None) if isinstance(x,dict) else None)
        df['SeverityL'] = df['Severity'].apply(lambda x: x.get('Label', None))
        df['SeverityN'] = df['Severity'].apply(lambda x: x.get('Normalized', None))
        df['SeverityN'] = pd.to_numeric(df['SeverityN'], errors='coerce')

        df.loc[df['passed'],'SeverityN'] = 0

        df['AwsAccountId'] = df['AwsAccountId'].astype(str).str.zfill(12)

        df = df.merge(self.df_accounts[['Name']], left_on='AwsAccountId', right_index=True, how='left')
        df.rename(columns={'Name' : 'AccountName'}, inplace=True)

        df['Standards'] = df['StandardsArn'].str.split(':').str[-1]
        df['StandardsControl'] = df['StandardsControlArn'].str.split(':').str[-1]

        df['ResType'] = df['Resources'].apply(lambda x: x[0].get('Type', None) if isinstance(x,list) else None)

        df['ResName'] = ''

        # Find Ressource Name
        #  IF name is after last : in ID
        res_filter = df['ResType'].isin([
            'AwsS3Bucket','AwsIamAccessKey', 'AwsLambdaFunction',
            'AwsApiGatewayV2Route', 'AwsElastiCacheCacheCluster'
        ])
        df.loc[res_filter,'ResName'] = df[res_filter]['Resources'].apply(lambda x: x[0]['Id'].split(':')[-1])

        # IF name is after last / in ID
        res_filter = df['ResType'].isin([
            'AwsCodeBuildProject',
            'AwsEcsTaskDefinition', 'AwsEcsCluster', 'AwsEcrRepository',
            'AwsEc2NetworkAcl', 'AwsEc2Volume', 'AwsEc2SecurityGroup', 'AwsCloudTrailTrail'
        ])
        df.loc[res_filter,'ResName'] = df[res_filter]['Resources'].apply(lambda x: x[0]['Id'].split('/')[-1])

        # IF name is in Tag Name
        res_filter = df['ResType'].isin(['AwsEc2Vpc', 'AwsEc2Subnet', 'AwsEfsFileSystem'])
        df.loc[res_filter,'ResName'] = df[res_filter]['Resources'].apply(lambda x: x[0].get('Tags',{}).get('Name','-'))


        self.df_findings = df.sort_values(by=['SeverityN', 'Id'], ascending=[False, True])
        logger.info(f'df_findings: Number of standards found {len(self.df_findings.index)}')
        return self


    #*************************************************
    #
    #*************************************************
    def calculate_controls_and_standards(self):
        """ Update Controls and Standards with Findings statistics"""

        if self.df_findings is None:
            self.load_findings()


        # Isolate Security Hub Findings
        df = self.df_findings[self.df_findings['ProductName'] == 'Security Hub']

        # Get list of accounts
        df_accounts = pd.DataFrame({'AwsAccountId' : df['AwsAccountId'].unique()})


        # Compile Controls stattus with Findings
        gb_std_ctrl = df.groupby(['Standards', 'AwsAccountId', 'StandardsControl'])

        df_std_ctrl = pd.DataFrame(index=gb_std_ctrl.groups.keys(),)
        df_std_ctrl.index.names = ['Standards', 'AwsAccountId', 'StandardsControl']
        df_std_ctrl['AccountName'] = gb_std_ctrl['AccountName'].first()
        df_std_ctrl['CheckCount'] = gb_std_ctrl['passed'].count()
        df_std_ctrl['CheckPass'] = gb_std_ctrl['passed'].sum()
        df_std_ctrl['CheckFail'] = df_std_ctrl['CheckCount'] - df_std_ctrl['CheckPass']


        # Create list of all Controls for all accounts
        df_controls = self.df_controls[['Standards','ControlStatus','StandardsControl', 'ControlId', 'SeverityRating']].copy()
        df_accounts['key'] = 1
        df_controls['key'] = 1
        df = pd.merge(left=df_accounts, right=df_controls, on='key').drop('key', axis=1)
        df.set_index(['Standards', 'AwsAccountId', 'StandardsControl'], inplace=True)

        # Merge with Findings results
        df = df.merge(df_std_ctrl, how='left', left_index=True, right_index=True)
        df['CheckCount'] = df['CheckCount'].fillna(0)
        df['CheckPass'] = df['CheckPass'].fillna(0)
        df['CheckFail'] = df['CheckFail'].fillna(0)
        df['ControlNoData'] = df['CheckCount'] == 0
        df['ControlActive'] = (df['CheckCount'] > 0) & (df['ControlStatus'] == 'ENABLED')
        df['ControlPassed'] = (df['CheckPass'] == df['CheckCount']) & df['ControlActive']
        df['ComplianceStatus'] = 'FAILED'
        df.loc[df['ControlPassed'], 'ComplianceStatus'] = 'PASSED'
        df.loc[df['ControlNoData'], 'ComplianceStatus'] = 'NO DATA'


        self.df_controls_results = df

        df['IsCritical'] = (df['SeverityRating'] == 'CRITICAL') & (df['ComplianceStatus'] == 'FAILED')
        df['IsHigh']     = (df['SeverityRating'] == 'HIGH') & (df['ComplianceStatus'] == 'FAILED')
        df['IsMedium']   = (df['SeverityRating'] == 'MEDIUM') & (df['ComplianceStatus'] == 'FAILED')
        df['IsLow']      = (df['SeverityRating'] == 'LOW') & (df['ComplianceStatus'] == 'FAILED')

        # Compile at the Standard level
        gb_std = df.groupby(['Standards', 'AwsAccountId'])
        df_std = pd.DataFrame(index=gb_std.groups.keys())
        df_std.index.names = ['Standards', 'AwsAccountId']
        df_std['AccountName'] = gb_std['AccountName'].first()
        df_std['Controls'] = gb_std['ControlStatus'].count()
        df_std['ControlsActive'] = gb_std['ControlActive'].sum()
        df_std['ControlsPassed'] = gb_std['ControlPassed'].sum()
        df_std['ControlsFailed'] = df_std['ControlsActive'] - df_std['ControlsPassed']
        df_std['Critical'] = gb_std['IsCritical'].sum()
        df_std['High'] = gb_std['IsHigh'].sum()
        df_std['Medium'] = gb_std['IsMedium'].sum()
        df_std['Low'] = gb_std['IsLow'].sum()
        df_std['Score'] = df_std['ControlsPassed'] / df_std['ControlsActive']
        df_std['ScoreTxt'] = df_std['Score'].apply(lambda x: f'{x * 100:.1f}%' if x is not None else '-')


        self.df_standards_results = df_std

        # print(self.df_standards_results)

        return self

    #*************************************************
    #
    #*************************************************
    def update_findings(self):
        """ Update Findings """
        self.load_findings()
        return self.calculate_controls_and_standards()


    #*************************************************
    #
    #*************************************************
    def modify_finding_workflow(self):
        """Display A Finding"""

        choices = ["NEW", "NOTIFIED", "RESOLVED", "SUPPRESSED"]

        print('Possible workflow status:')
        print('   1 - NEW')
        print('   2 - NOTIFIED')
        print('   3 - RESOLVED')
        print('   4 - SUPPRESSED')
        choice = o7i.input_int('Enter your choice:')

        if choice is None:
            return

        if choice < 1 or choice > len(choices):
            print('Invalid choice')
            return

        new_status = choices[choice - 1]

        confirm = o7i.is_it_ok(f'Confirm setting workflow status to {new_status}')
        if confirm is False:
            return

        response = self.client.batch_update_findings(
            FindingIdentifiers=[
                {
                    'Id': self.finding['Id'],
                    'ProductArn': self.finding['ProductArn']
                },
            ],
            Workflow={ 'Status': new_status}
        )
        pprint.pprint(response)



    #*************************************************
    #
    #*************************************************
    def display_standard(self):
        """Display Security Hub"""

        standards = self.standard.name

        print('')
        print(f'Name: {self.standard["Name"]}')
        print(f'Description: {self.standard["Description"]}')
        print(f'Standards: {standards}')
        print('')
        print(f'Status: {self.standard["StandardsStatus"]}')
        print('')



        df_results = self.df_standards_results.loc[standards] if self.df_standards_results is not None else None

        if df_results is not None:

            self.findings_per_account = df_results.reset_index()

            params = TableParam(
                with_footer = True,
                columns = [
                    ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
                    ColumnParam(title = 'Account Id',  type = 'str',  data_col = 'AwsAccountId'),
                    ColumnParam(title = 'Account Name',  type = 'str',  data_col = 'AccountName'),
                    ColumnParam(title = 'Active',     type = 'int',  data_col = 'ControlsActive', footer = 'sum'),
                    ColumnParam(title = 'Passed',     type = 'int',  data_col = 'ControlsPassed', footer = 'sum'),
                    ColumnParam(title = 'Failed',     type = 'int',  data_col = 'ControlsFailed', footer = 'sum'),
                    ColumnParam(title = 'Critical',     type = 'int',  data_col = 'Critical', footer = 'sum'),
                    ColumnParam(title = 'High',     type = 'int',  data_col = 'High', footer = 'sum'),
                    ColumnParam(title = 'Medium',     type = 'int',  data_col = 'Medium', footer = 'sum'),
                    ColumnParam(title = 'Low',     type = 'int',  data_col = 'Low', footer = 'sum'),

                    ColumnParam(title = 'Score', type = 'percent',  data_col = 'Score', alarm_lo=0.60, warning_lo=0.90, footer = 'avg'),

                ]

            )
            Table(params, self.findings_per_account.to_dict(orient='records')).print()
        else:
            print('No results were compiled, did you load the findings?')

        print('')

        # df = self.df_controls[self.df_controls['Standards'] == standards] if self.df_controls_results is not None else None

        # params = TableParam(
        #     columns = [
        #         ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
        #         ColumnParam(title = 'ControlId',  type = 'str',  data_col = 'ControlId'),
        #         ColumnParam(title = 'Title',     type = 'str',  data_col = 'Title'),
        #         #ColumnParam(title = 'Status',     type = 'str',  data_col = 'ComplianceStatus', format= 'aws-status'),
        #         ColumnParam(title = 'Severity',     type = 'str',  data_col = 'SeverityRating'),
        #         # ColumnParam(title = 'Check Count',     type = 'int',  data_col = 'CheckCount'),
        #         # ColumnParam(title = 'Pass',     type = 'int',  data_col = 'CheckPass')
        #     ]
        # )
        # Table(params, df.to_dict(orient='records')).print()

        # print()

    #*************************************************
    #
    #*************************************************
    def display_control(self):
        """Display Security Hub"""

        # print(self.control)
        print(f'Standard: {self.standard["Name"]}')
        print(f'Id: {self.control["ControlId"]}')
        print('')
        print(f'Title: {self.control["Title"]}')
        print(f'Severity: {self.control["SeverityRating"]}')
        print(f'Compliance Status: {self.control["ComplianceStatus"]}')
        print('')
        print('Description:')
        print(self.control["Description"])
        print('')
        print(f'RemediationUrl: {self.control["RemediationUrl"]}')
        print('')

        self.df_menu_findings = self.df_findings[self.df_findings['StandardsControlArn'] == self.control['StandardsControlArn']]

        params = TableParam(
            columns = [
                ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
                ColumnParam(title = 'Status',     type = 'str',  data_col = 'Status', format= 'aws-status'),
                ColumnParam(title = 'Account',  type = 'str',  data_col = 'AwsAccountId'),
                ColumnParam(title = 'Region',  type = 'str',  data_col = 'Region')
            ]
        )
        Table(params, self.df_menu_findings.to_dict(orient='records')).print()

        print()



    #*************************************************
    #
    #*************************************************
    def display_per_account(self):
        """Display Security Hub"""

        print('')
        if self.df_findings is None:
            print('Findings are not loaded')
            return

        self.findings_per_account = self.compile_findings_per_accounts()

        params = TableParam(
            with_group = True,
            columns = [
                ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
                ColumnParam(title = 'Account',     type = 'str',  data_col = 'AwsAccountId'),
                ColumnParam(title = 'Account Name',     type = 'str',  data_col = 'AccountName'),
                ColumnParam(title = 'Critical'   ,  type = 'int',  data_col = 'Critical', critical_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'High'   ,  type = 'int',  data_col = 'High', alarm_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'Medium'   ,  type = 'int',  data_col = 'Medium', warning_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'Low'   ,  type = 'int',  data_col = 'Low', footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'High'   ,  type = 'int',  data_col = 'GuardDutyHigh', alarm_hi=1, footer = 'sum', group = "GuardDuty"),
                ColumnParam(title = 'Low'   ,  type = 'int',  data_col = 'GuardDutyLow', warning_hi=1, footer = 'sum', group = "GuardDuty"),
                ColumnParam(title = 'Findings'   ,  type = 'int',  data_col = 'Other', footer = 'sum', group = "Other"),

            ]
        )
        standards = self.df_standards[self.df_standards['StandardsStatus'] == 'READY'].copy()
        for index, row in standards.iterrows():
            std_short = row['Short']
            params.columns.append(
                ColumnParam(title = std_short, type = 'percent',  data_col = std_short, alarm_lo=0.60, warning_lo=0.90, footer = 'avg', group = "Standards")
            )

        Table(params, self.findings_per_account.to_dict(orient='records')).print()

        print()


    #*************************************************
    #
    #*************************************************
    def display_all_findings_next_page(self, page : int = None):
        """Display findings next page"""
        if page is None:
            self.finding_menu_index = self.finding_menu_index + self.FINDINGS_PAGE_SIZE
        else :
            self.finding_menu_index = page * self.FINDINGS_PAGE_SIZE

    def display_all_findings_prev_page(self):
        """Display findings next page"""
        self.finding_menu_index = max(self.finding_menu_index - self.FINDINGS_PAGE_SIZE,0)


    #*************************************************
    #
    #*************************************************
    def display_all_findings(self):
        """Display Security Hub"""

        print('')

        if self.df_findings is None:
            print('Findings are not loaded')
            print()
            return

        df = self.df_menu_findings
        if self.account is not None:
            print(f'Filtering by account: {self.account["AwsAccountId"]} - {self.account["AccountName"]}')
            df = df[df['AwsAccountId'] == self.account["AwsAccountId"]]

        if self.standard is not None:
            standards = self.standard.name
            print(f'Filtering by standard: {standards}')
            df = df[df['Standards'] == standards]

        last_finding = self.finding_menu_index + self.FINDINGS_PAGE_SIZE
        print(f'Findings {self.finding_menu_index} to {last_finding}')
        self.df_menu_findings = df.copy()
        self.df_menu_findings['i'] = range(1, len(self.df_menu_findings) + 1)
        params = TableParam(
            columns = [
                ColumnParam(title = 'id',          type = 'str',    min_width = 4, data_col = 'i' ),
                ColumnParam(title = 'Source',     type = 'str',  data_col = 'ProductName'),
                ColumnParam(title = 'Account',     type = 'str',  data_col = 'AwsAccountId'),
                ColumnParam(title = 'Region',     type = 'str',  data_col = 'Region'),
                ColumnParam(title = 'Severity',     type = 'str',  data_col = 'SeverityL',  max_width = 4),
                ColumnParam(title = 'ResType',   type = 'str',  data_col = 'ResType', max_width = 15),
                ColumnParam(title = 'ResName',   type = 'str',  data_col = 'ResName', max_width = 15),
                ColumnParam(title = 'Title',     type = 'str',  data_col = 'Title'),
            ]
        )
        Table(params, self.df_menu_findings[self.finding_menu_index:last_finding].to_dict(orient='records')).print()

        print()

    #*************************************************
    #
    #*************************************************
    def display_finding(self):
        """Display A Finding"""

        print('')
        print(f'Source: {self.finding["ProductName"]}')
        print(f'Account / Region: {self.finding["AwsAccountId"]} / {self.finding["Region"]}')
        print(f'Type: {self.finding["Types"]}')
        print()
        print(f'Title: {self.finding["Title"]}')
        print()
        print(f'Description: {self.finding["Description"]}')
        print()
        print('Severity')
        pprint.pprint(self.finding['Severity'])
        print()
        print('Remediation')
        pprint.pprint(self.finding['Remediation'], depth=4)
        print()
        print('Resources')
        pprint.pprint(self.finding['Resources'])
        print()
        print('Compliance')
        pprint.pprint(self.finding['Compliance'])
        print()
        print('Workflow')
        pprint.pprint(self.finding['Workflow'])


    #*************************************************
    #
    #*************************************************
    def display_overview(self):
        """Display Security Hub"""

        if self.df_controls is None :
            self.load_standard_controls()

        print('')
        print('Available Standards')
        params = TableParam(
            with_group = True,
            columns = [
                ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
                ColumnParam(title = 'Short',     type = 'str',  data_col = 'Short'),
                ColumnParam(title = 'Name',     type = 'str',  data_col = 'Name'),
                ColumnParam(title = 'Status',     type = 'str',  data_col = 'StandardsStatus'),
                ColumnParam(title = 'Count',     type = 'int',  data_col = 'ControlsCount', group = 'Controls'),
                ColumnParam(title = 'Disabled',     type = 'int',  data_col = 'ControlDisabled', group = 'Controls'),
            ]
        )
        Table(params, self.df_standards.to_dict(orient='records')).print()

        print('')
        if self.df_findings is not None:

            findings_compile = self.compile_findings_per_accounts()
            print('Number of affected accounts: ', len(findings_compile.index))
            print('Failed Findings')
            print(f'   Critical: {findings_compile["Critical"].sum()}')
            print(f'   High: {findings_compile["High"].sum()}')
            print(f'   Medium: {findings_compile["Medium"].sum()}')
            print(f'   Low: {findings_compile["Low"].sum()}')
            print(f'   Total: {findings_compile["Total"].sum()}')


            print('')
            print('Top 10 Findings')
            params = TableParam(
                columns = [
                    ColumnParam(title = 'Source',    type = 'str',  data_col = 'ProductName'),
                    ColumnParam(title = 'Account',   type = 'str',  data_col = 'AwsAccountId'),
                    ColumnParam(title = 'Region',     type = 'str',  data_col = 'Region'),
                    ColumnParam(title = 'AccountName',   type = 'str',  data_col = 'AccountName'),
                    ColumnParam(title = 'Severity',  type = 'int',  data_col = 'SeverityN', alarm_hi = 70.0, warning_hi=40.0),
                    ColumnParam(title = 'Title',     type = 'str',  data_col = 'Title'),
                ]
            )
            Table(params, self.df_findings[0:10].to_dict(orient='records')).print()
        else:
            print('Findings not loaded. Use "l" to load')
        print()




    #*************************************************
    #
    #*************************************************
    def to_excel(self):
        """Save to Excel"""

        filename= f"aws-securityhub-{datetime.datetime.now().isoformat()[0:19].replace(':','-')}.xlsx"
        with pd.ExcelWriter(filename) as writer: # pylint: disable=abstract-class-instantiated

            df_parameters = pd.DataFrame([
                {'Parameter' : 'Date', 'Value' : datetime.datetime.now().isoformat()},
                {'Parameter' : 'Account', 'Value' : o7cli.sts.Sts(session=self.session).get_account_id()}
            ])
            df_parameters.to_excel(writer, sheet_name="Parameters")

            self.df_standards.to_excel(writer, sheet_name="Standards")
            self.df_controls.to_excel(writer, sheet_name="Controls")
            #self.df_accounts.to_excel(writer, sheet_name="Accounts")


            if self.df_findings is not None:
                self.df_findings.to_excel(writer, sheet_name="Findings")

            if self.df_standards_results is not None:
                self.df_standards_results.to_excel(writer, sheet_name="Standards_Results")
                self.df_controls_results.to_excel(writer, sheet_name="Controls_Results")


        print(f"Security Hub saved in file: {filename}")


    #*************************************************
    #
    #*************************************************
    def from_excel(self, filename):
        """Save to Excel"""

        print(f"Loading file: {filename}")
        self.df_standards = pd.read_excel(filename, sheet_name='Standards')
        self.df_standards.set_index('Standards', inplace=True)

        self.df_controls = pd.read_excel(filename, sheet_name='Controls')
        self.df_accounts = pd.read_excel(filename, sheet_name='Accounts')
        self.df_findings = pd.read_excel(filename, sheet_name='Findings')


    #*************************************************
    #
    #*************************************************
    def write_html_report(self):
        """Save HTML report"""

        filename= f"aws-securityhub-report-{datetime.datetime.now().isoformat()[0:19].replace(':','-')}.html"
        filename= f"aws-securityhub-report-test.html"
        report = self.generate_html_report()

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as htmlfile:
                htmlfile.write(report)
            print(f"Security Hub report saved in file: {filename}")

        except IOError:
            print(f"Count not write to: {filename}")

        return self

    #*************************************************
    #
    #*************************************************
    def compile_findings_per_accounts(self) -> pd.DataFrame:
        """ Compile Findings per Account"""

        df = self.df_findings[self.df_findings['SeverityN'] > 0][['AwsAccountId', 'AccountName','ProductName', 'SeverityN', 'SeverityL']].copy()


        df['IsSecurityHub'] = (df['ProductName'] == 'Security Hub')
        df['IsGuardDuty']      = (df['ProductName'] == 'GuardDuty')
        df['IsOther'] = ~(df['IsSecurityHub'] | df['IsGuardDuty'])

        df['IsCritical'] = df['IsSecurityHub'] & (df['SeverityN'] >= 80)
        df['IsHigh']     = df['IsSecurityHub'] & (df['SeverityN'] >= 60) & (df['SeverityN'] < 80)
        df['IsMedium']   = df['IsSecurityHub'] & (df['SeverityN'] >= 40) & (df['SeverityN'] < 60)
        df['IsLow']      = df['IsSecurityHub'] & (df['SeverityN'] < 40)

        df['IsGuardDutyHigh']  = df['IsGuardDuty'] & (df['SeverityL'] == 'HIGH')
        df['IsGuardDutyLow']   = df['IsGuardDuty'] & ~df['IsGuardDutyHigh']

        gb = df.groupby(['AwsAccountId'])
        df_ret = pd.DataFrame(index=gb.groups.keys())
        df_ret.index.names = ['AwsAccountId']
        df_ret['AccountName'] = gb['AccountName'].first()

        df_ret['Total'] = gb['SeverityN'].count()

        df_ret['Critical'] = gb['IsCritical'].sum()
        df_ret['High'] = gb['IsHigh'].sum()
        df_ret['Medium'] = gb['IsMedium'].sum()
        df_ret['Low'] = gb['IsLow'].sum()

        df_ret['GuardDuty'] = gb['IsGuardDuty'].sum()
        df_ret['GuardDutyHigh'] = gb['IsGuardDutyHigh'].sum()
        df_ret['GuardDutyLow'] = gb['IsGuardDutyLow'].sum()

        df_ret['Other'] = gb['IsOther'].sum()

        standards = self.df_standards[self.df_standards['StandardsStatus'] == 'READY']
        for index, row in standards.iterrows():
            std_short = row['Short']
            df_std_results = self.df_standards_results.loc[index].copy()
            df_std_results.reset_index(inplace=True)
            df_std_results.set_index('AwsAccountId', inplace=True)
            df_ret[std_short] = df_std_results['Score']

        df_ret.reset_index(inplace=True)


        return df_ret



    #*************************************************
    #
    #*************************************************
    def generate_html_report(self):
        """Generate HTML Report"""

        print("Generating Security Hub HTML Report")

        if self.df_controls is None :
            self.load_standard_controls()


        # self.update_findings()
        self.calculate_controls_and_standards()
        stats_per_account = self.compile_findings_per_accounts()



        report = o7hr.HtmlReport(name='Security Hub')
        report.greeting = 'Hi Security Chief'


        params = TableParam(
            with_footer = True,
            with_group = True,
            columns = [
                ColumnParam(title = 'Account',     type = 'str',  data_col = 'AwsAccountId'),
                ColumnParam(title = 'Account Name',     type = 'str',  data_col = 'AccountName'),
                ColumnParam(title = 'Critical'   ,  type = 'int',  data_col = 'Critical', critical_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'High'   ,  type = 'int',  data_col = 'High', alarm_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'Medium'   ,  type = 'int',  data_col = 'Medium', warning_hi=1, footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'Low'   ,  type = 'int',  data_col = 'Low', footer = 'sum', group = "Security Hub"),
                ColumnParam(title = 'GuardDuty'   ,  type = 'int',  data_col = 'GuardDuty', alarm_hi=1, footer = 'sum'),
            ]
        )

        standards = self.df_standards[self.df_standards['StandardsStatus'] == 'READY'].copy()
        for index, row in standards.iterrows():
            std_short = row['Short']
            params.columns.append(
                ColumnParam(title = std_short, type = 'percent',  data_col = std_short, alarm_lo=0.60, warning_lo=0.90, footer = 'avg', group = "Standards")
            )


        findigs_per_account_html = Table(params, stats_per_account.to_dict(orient='records')).generate_html()
        Table(params, stats_per_account.to_dict(orient='records')).print()
        print('')
        report.add_section(title='Failed Findings per Account', html=findigs_per_account_html)

        # for index, row in standards.iterrows():

        #     df = self.df_standards_results.loc[index].copy()
        #     df.reset_index(inplace=True)
        #     # df['AwsAccountId'] = df['AwsAccountId'].astype(str).str.zfill(12)

        #     params = TableParam(
        #         title = row['Name'],
        #         columns = [
        #             ColumnParam(title = 'Account',     type = 'str',  data_col = 'AwsAccountId'),
        #             ColumnParam(title = 'Account Name',     type = 'str',  data_col = 'AccountName'),
        #             ColumnParam(title = 'Controls',     type = 'int',  data_col = 'Controls'),
        #             ColumnParam(title = 'Active',     type = 'int',  data_col = 'ControlsActive'),
        #             ColumnParam(title = 'Passed',     type = 'int',  data_col = 'ControlsPassed'),
        #             ColumnParam(title = 'Failed',     type = 'int',  data_col = 'ControlsFailed'),
        #             ColumnParam(title = 'Score',     type = 'str',  data_col = 'ScoreTxt')
        #         ]
        #     )
        #     standard_html = Table(params, df.to_dict(orient='records')).generate_html()
        #     Table(params, df.to_dict(orient='records')).print()
        #     print('')
        #     report.add_section(title=f'Compliance for standard : {row["Name"]}', html=standard_html)


        findings = self.df_findings[self.df_findings['SeverityN'] > 0].copy()
        findings['Started'] = findings['FirstObservedAt'].str.slice(0,10)

        params = TableParam(
            columns = [
                ColumnParam(title = 'Source',     type = 'str',  data_col = 'ProductName'),
                ColumnParam(title = 'Account',     type = 'str',  data_col = 'AwsAccountId'),
                ColumnParam(title = 'Region',     type = 'str',  data_col = 'Region'),
                ColumnParam(title = 'Severity',  type = 'int',  data_col = 'SeverityN', critical_hi=90, alarm_hi = 70.0, warning_hi=50.0),
                ColumnParam(title = 'Started',   type = 'str',  data_col = 'Started'),
                ColumnParam(title = 'Title',     type = 'str',  data_col = 'Title'),
            ]
        )
        findigs_html = Table(params, findings[0:25].to_dict(orient='records')).generate_html()
        Table(params, findings[0:10].to_dict(orient='records')).print()
        print('')
        report.add_section(title='Top 25 Failed Findings', html=findigs_html)

        return report.generate()

    #*************************************************
    #
    #*************************************************
    def menu_finding(self, index):
        """Specific Finding menu"""


        if  not 0 < index <= len(self.df_menu_findings.index):
            return self

        self.finding = self.df_menu_findings.iloc[index-1]

        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub - Finding Details', title_extra=self.session_info(), compact=True)

        obj.add_option(o7m.Option(
            key='r',
            name='Raw',
            short='Raw',
            callback=lambda : print(self.finding)
        ))
        obj.add_option(o7m.Option(
            key='w',
            name='Update Workflow',
            short='Workflow',
            callback=self.modify_finding_workflow
        ))

        obj.display_callback = self.display_finding
        obj.loop()

        return self

    #*************************************************
    #
    #*************************************************
    def menu_finding_for_an_account(self, index):
        """Findigns per account  menu"""

        if  not 0 < index <= len(self.findings_per_account.index):
            return self


        self.account = self.findings_per_account.iloc[index-1]


        self.menu_all_finding()
        self.account = None



    #*************************************************
    #
    #*************************************************
    def menu_per_account(self):
        """ Findings per account menu"""



        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub - Findings per accounts', title_extra=self.session_info(), compact=False)
        obj.add_option(o7m.Option(
            key='int',
            name='Findings for an account',
            short='Details',
            callback=self.menu_finding_for_an_account
        ))

        obj.display_callback = self.display_per_account
        obj.loop()

        return self


    #*************************************************
    #
    #*************************************************
    def menu_all_finding(self):
        """Organization menu"""


        self.df_menu_findings = self.df_findings

        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub - All Findings', title_extra=self.session_info(), compact=True)
        obj.add_option(o7m.Option(
            key='int',
            name='Details for a Finding',
            short='Details',
            callback=self.menu_finding
        ))
        obj.add_option(o7m.Option(
            key='s',
            name='Start',
            short='Start',
            wait=False,
            callback=lambda : self.display_all_findings_next_page(0)
        ))
        obj.add_option(o7m.Option(
            key='n',
            name='Next',
            short='Next',
            wait=False,
            callback=self.display_all_findings_next_page
        ))
        obj.add_option(o7m.Option(
            key='p',
            name='Previous',
            short='Prev',
            wait=False,
            callback=self.display_all_findings_prev_page
        ))

        obj.display_callback = self.display_all_findings
        obj.loop()

        return self

    #*************************************************
    #
    #*************************************************
    def menu_control(self, index):
        """Organization menu"""

        if self.standard.name not in self.dfs_controls.keys() :
            return self

        df_controls = self.dfs_controls[self.standard.name]

        if  not 0 < index <= len(df_controls.index):
            return self

        self.control = df_controls.iloc[index-1]

        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub - Control Details', title_extra=self.session_info(), compact=False)

        obj.add_option(o7m.Option(
            key='int',
            name='Details for a Finding',
            short='Details',
            callback=self.menu_finding
        ))

        obj.display_callback = self.display_control
        obj.loop()

        return self

    #*************************************************
    #
    #*************************************************
    def menu_standard(self, index):
        """Standard menu"""

        if  not 0 < index <= len(self.df_standards.index):
            return self

        self.standard = self.df_standards.iloc[index-1]

        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub - Standard Details', title_extra=self.session_info(), compact=False)

        obj.add_option(o7m.Option(
            key='r',
            name='Raw',
            short='Raw',
            callback=lambda : print(self.standard)
        ))

        obj.add_option(o7m.Option(
            key='int',
            name='Details for a Account',
            short='Details',
            callback=self.menu_finding_for_an_account
        ))


        obj.display_callback = self.display_standard
        obj.loop()

        self.standard = None
        return self

    #*************************************************
    #
    #*************************************************
    def menu_overview(self):
        """Organization menu"""


        obj = o7m.Menu(exit_option = 'b', title='Secutity Hub Overview', title_extra=self.session_info(), compact=False)

        obj.add_option(o7m.Option(
            key='l',
            name='Load Findings',
            short='Load',
            callback=self.update_findings
        ))
        obj.add_option(o7m.Option(
            key='a',
            name='View per accounts',
            short='Accounts',
            callback=self.menu_per_account
        ))
        obj.add_option(o7m.Option(
            key='f',
            name='View All Findings',
            short='Findings',
            callback=self.menu_all_finding
        ))
        obj.add_option(o7m.Option(
            key='x',
            name='Save To Excel',
            short='To Excel',
            callback=self.to_excel
        ))
        obj.add_option(o7m.Option(
            key='html',
            name='Write HTML Report',
            short='HTML',
            callback=self.write_html_report
        ))


        obj.add_option(o7m.Option(
            key='int',
            name='Details for a Standard',
            short='Details',
            callback=self.menu_standard
        ))


        obj.display_callback = self.display_overview
        obj.loop()

        return self

#*************************************************
#
#*************************************************
def menu(**kwargs):
    """Run Main Menu"""
    SecurityHub(**kwargs).menu_overview()


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', o7t.get_width())
    pd.set_option('display.max_colwidth',  20)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    the_obj = SecurityHub()
    the_obj.menu_overview()
    exit(0)

    # the_obj.load_standard_controls()
    # the_obj.load_findings()
    # the_obj.to_excel()
    # exit(0)

    # the_obj.menu_overview()
    the_obj.from_excel(filename='aws-securityhub-2024-01-10T00-34-54.xlsx')

    # the_obj.calculate_controls_and_standards()

    the_report = the_obj.generate_html_report()

    # print('*'*80)
    # print(the_report)
    # print('*'*80)

    # the_obj.to_excel()

    #--------------------------------
    # Save to File
    #--------------------------------
    filname = 'security_hub.cache.html'
    try:
        with open(filname, 'w', newline='', encoding='utf-8') as htmlfile:
            htmlfile.write(the_report)

    except IOError:
        print(f"Count not write to: {filname}")
