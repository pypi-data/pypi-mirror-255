"""Module to explore AWS costs"""
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
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


#--------------------------------
#
#--------------------------------
import datetime
import logging

import pandas as pd

import botocore.exceptions

import o7util.input
import o7util.report
import o7util.terminal as o7t

import o7cli.cloudwatch

import o7lib.aws.base
import o7cli.organizations


pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

logger=logging.getLogger(__name__)


#*************************************************
#
#*************************************************
class CostExplorer(o7lib.aws.base.Base):
    """Class to Explore AWS costs"""

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.cost_explorer = self.session.client(
            'ce',
            config=botocore.config.Config(connect_timeout = 5, retries={'max_attempts': 0})
        )

        self.df_accounts = None
        self.tags = None

        self.group_type   : str = None
        self.group_key    : str = None
        self.filters      : list= []

        self.df_costs     :  pd.DataFrame = None
        self.df_costs_summarize : pd.DataFrame = None

    #*************************************************
    #
    #*************************************************
    def conformity_report(self, report : o7util.report.Report = None):
        """Generate a conformity report section"""

        section_name = 'Cost Explorer & Billing'
        if report is None:
            report = o7util.report.Report('Account Conformity Report', section_name=section_name)
        else:
            report.add_section(section_name)


        o7cli.cloudwatch.Cloudwatch(session=self.session).report_alarm_sns_email(
            report, name = 'Billing', namespace='AWS/Billing', metric_name='EstimatedCharges'
        )

        report.add_test(name="Cost Explorer Status", critical=True)
        try:
            tags = self.load_tags()
        except botocore.exceptions.ClientError:
            report.TestFail("Not Enable in Account")
            return False

        report.test_pass("Enable")

        report.add_test(name="Cost Explorer Tag", critical=True)
        if len(tags) == 0:
            report.test_fail("No Tags Found")
            return False

        report.test_pass(f'Found {len(tags)} Tags')

        report.add_test(name="Tag PROJECT created", critical=False)
        if 'PROJECT' in tags :
            report.test_pass()

        report.test_fail()


        return True


    #*************************************************
    #
    #*************************************************
    def get_cost_and_usage_all_pages(self, params : dict) -> pd.DataFrame:
        """Get all pages of Cost and Usage"""

        done=False
        results = []

        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce/client/get_cost_and_usage.html
            response = self.cost_explorer.get_cost_and_usage(**params)
            if 'NextPageToken' in response:
                params['NextPageToken'] = response['NextPageToken']
            else:
                done = True

            results.extend(response.get('ResultsByTime',[]))

        return results



    #*************************************************
    #
    #*************************************************
    def update_costs(self, days : int =30) -> pd.DataFrame:
        """Upate Cost information using the selected option"""

        self.df_costs = self.get_cost(days=days)
        self.df_costs_summarize = self.summarize_cost(self.df_costs, key=self.group_key)

        # For Linked Account, add the account name
        if self.group_key == 'LINKED_ACCOUNT':
            df_accounts = self.load_accounts()
            self.df_costs_summarize = pd.merge(
                left=self.df_costs_summarize,
                left_on='LINKED_ACCOUNT',
                right=df_accounts[['Id', 'Name']],
                right_on='Id',
                how='outer'
            )
            self.df_costs_summarize = self.df_costs_summarize.drop('Id', axis=1)

            # Set name in the 2nd colum
            columns = self.df_costs_summarize.columns.tolist()
            last_column = columns.pop(-1)
            columns.insert(1, last_column)
            self.df_costs_summarize =  self.df_costs_summarize[columns]


    #*************************************************
    #
    #*************************************************
    def get_cost(self, days : int =30) -> pd.DataFrame:
        """Get Cost information using the selected option"""

        df_cost = self.get_cost_total(days=days, filters=self.filters)

        if self.group_type is not None:
            df_costs_grouped = self.get_cost_grouped(
                group_type=self.group_type,
                group_key=self.group_key,
                filters=self.filters,
                days=days
            )
            df_cost = df_cost.join(df_costs_grouped)

        return df_cost


    #*************************************************
    #
    #*************************************************
    def get_cost_total(self, days : int =30, filters : list = None) -> pd.DataFrame:
        """Get Cost information without grouping"""

        now = datetime.datetime.now()
        date_start = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

        logger.info(f"Getting AWS Total Cost from {date_start} to {date_end}")
        total_costs = []

        params={
                'TimePeriod':{
                        'Start': date_start,
                        'End': date_end
                },
                'Granularity' : 'DAILY',
                'Metrics' : ['NetAmortizedCost'],
                'Filter' : {
                    'Not' : {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': ['Credit', 'Refund'],
                            'MatchOptions': ['EQUALS']
                        }
                    },
                    'Not' : {
                        'Dimensions': {
                            'Key': 'SERVICE',
                            'Values': ['Tax'],
                            'MatchOptions': ['EQUALS']
                        }
                    }

                }
        }

        if len(filters) > 0:
            _filters = filters.copy()
            _filters.append(params['Filter'].copy())
            params['Filter'] = {'And' : _filters}

        results = self.get_cost_and_usage_all_pages(params)
        # pprint.pprint(results)

        # Process all entries to store in Pandas dataframe
        for result in results :

            dt_day = datetime.datetime.strptime(result['TimePeriod']['Start'], "%Y-%m-%d")
            total_costs.append({
                "Date" : dt_day,
                "Total" : float(result['Total']['NetAmortizedCost']['Amount']),
            })

        df = pd.DataFrame(data = total_costs)
        df.set_index('Date', inplace=True)

        return df


    #*************************************************
    #
    #*************************************************
    def get_cost_grouped(self,
        days : int = 30,
        group_type : str = 'TAG',
        group_key : str = 'Project',
        filters : list = None
    ) -> pd.DataFrame:
        """Get Cost information with grouping"""

        now = datetime.datetime.now()
        date_start = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

        logger.info(f"Getting AWS Total Cost from {date_start} to {date_end}")
        grouped_costs = []

        params={
                'TimePeriod':{
                        'Start': date_start,
                        'End': date_end
                },
                'Granularity' : 'DAILY',
                'Metrics' : ['NetAmortizedCost'],
                'GroupBy' : [],
                'Filter' : {
                    'Not' : {
                        'Dimensions': {
                            'Key': 'RECORD_TYPE',
                            'Values': ['Credit', 'Refund'],
                            'MatchOptions': ['EQUALS']
                        }
                    },
                    'Not' : {
                        'Dimensions': {
                            'Key': 'SERVICE',
                            'Values': ['Tax'],
                            'MatchOptions': ['EQUALS']
                        }
                    }
                }
        }

        params['GroupBy'].append({'Type': group_type, 'Key': group_key})

        if len(filters) > 0:
            _filters = filters.copy()
            _filters.append(params['Filter'].copy())
            params['Filter'] = {'And' : _filters}

        results = self.get_cost_and_usage_all_pages(params)

        # Process all entries to store in Pandas dataframe
        for result in results :

            dt_day = datetime.datetime.strptime(result['TimePeriod']['Start'], "%Y-%m-%d")
            for group in result.get('Groups',[]) :

                key = group['Keys'][0]
                if group_type == 'TAG':
                    key = key.removeprefix(f'{group_key}$').lower()

                grouped_costs.append({
                    "Date" : dt_day,
                    key : float(group['Metrics']['NetAmortizedCost']['Amount']),
                })


        df = pd.DataFrame(data = grouped_costs)
        #print(df)
        df = df.fillna(0.0).groupby('Date').sum()

        # Sort columns by total cost
        sorted_columns = df.sum().sort_values(ascending=False).index
        df = df[sorted_columns]

        return df

    #*************************************************
    #
    #*************************************************
    def load_tags(self):
        """Load cost of tags"""

        if self.tags is not None:
            return self.tags

        # print(f"Getting AWS Cost Tags")
        now = datetime.datetime.now()
        date_start = (now - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        date_end = now.strftime('%Y-%m-%d')

        self.tags = []
        param={
                'TimePeriod':{
                        'Start': date_start,
                        'End': date_end
                },
        }
        response = self.cost_explorer.get_tags(**param)

        self.tags.extend(response.get('Tags',[]))

        return self.tags

    #*************************************************
    #
    #*************************************************
    def load_accounts(self):
        """Get list of accounts"""

        if self.df_accounts is None:
            linked_accounts = [{'Id' : 'na', 'Name' : 'na', 'Email' : 'na', 'Status' : 'na'}]
            try:
                linked_accounts = o7cli.organizations.Organizations(session=self.session).load_accounts().accounts
            except botocore.exceptions.ClientError:
                pass

            self.df_accounts = pd.DataFrame(linked_accounts)

        return self.df_accounts



    #*************************************************
    #
    #*************************************************
    def summarize_cost(self, df_costs : pd.DataFrame, key : str = 'Key') -> pd.DataFrame:
        """Compile cost by group"""

        #-----------------------
        # Max number of days
        #-----------------------
        days = (datetime.datetime.now() - df_costs.index.min()).days
        logger.info(f'Compile for {days} days')
        columns = {'Total': f'{days} Day Sum', 'Avr' : f'{days} Day Avr', 'Max' : f'{days} Day Max'}
        sort_key = f'{days} Day Sum'


        df_daily = df_costs.stack().reset_index()
        df_daily.columns = ['Date',key, 'Cost']
        df_daily.set_index('Date', inplace=True)

        #-----------------------
        # Compile on full range
        #-----------------------
        day_30_costs = df_daily.groupby(key).agg(
            Total=('Cost','sum'),
            Max=('Cost','max'),
            Avr=('Cost','mean')
        )
        day_30_costs = day_30_costs.rename(columns=columns)

        #-----------------------
        # Compile on 7 days
        #-----------------------
        day7 = datetime.datetime.now() - datetime.timedelta(days=8)
        columns = {'Total': '7 Day Sum', 'Avr' : '7 Day Avr'}

        day_7_costs = df_daily.loc[day7:]
        day_7_costs = day_7_costs.groupby(key).agg(
            Total=('Cost','sum'),
            Avr=('Cost','mean')
        )
        day_7_costs = day_7_costs.rename(columns=columns)

        #-----------------------
        # Compile on last day
        #-----------------------
        yesterday = datetime.datetime.now() - datetime.timedelta(days=2)

        columns = {'Total': 'Yesterday'}
        yesterday_costs = df_daily.loc[yesterday:]
        yesterday_costs = yesterday_costs.groupby(key).agg(
            Total=('Cost','sum')
        ).rename(columns=columns)


        summarized_costs = pd.concat([day_30_costs, day_7_costs, yesterday_costs], axis=1, join="outer")
        summarized_costs = summarized_costs.sort_values(by=[sort_key], ascending=False)
        summarized_costs = summarized_costs.reset_index()

        return summarized_costs

    #*************************************************
    # {'Dimensions': {'Key': 'LINKED_ACCOUNT', 'Values': ['625257959362'], 'MatchOptions': ['EQUALS']}}
    # {'Tags':        {'Key': 'Project', 'Values': ['dev'], 'MatchOptions': ['EQUALS']}}
    #*************************************************
    def filters_str(self) -> str:
        """Return a string that represent the filters"""

        if len(self.filters) == 0:
            return 'All'

        rets = []
        for _filter in self.filters:
            if 'Dimensions' in _filter:
                rets.append(f"{_filter['Dimensions']['Key']}={_filter['Dimensions']['Values'][0]}")
            if 'Tags' in _filter:
                rets.append(f"{_filter['Tags']['Key']}={_filter['Tags']['Values'][0]}")

        return ','.join(rets)


    #*************************************************
    #
    #*************************************************
    def display_daily(self, costs : pd.DataFrame):
        """Display project summary"""

        self.console_title(left='Costs by Days')


        print(f"Grouping by {self.group_type} : {self.group_key}")
        print(f"Filters      : {self.filters_str()}")
        print("-" * o7t.get_width())
        print(costs)


    #*************************************************
    #
    #*************************************************
    def menu_tag(self) -> str:
        """Return a selected tag"""

        tags = self.load_tags()

        while True :

            self.console_title(left='Avalable Costing Tags')
            print("-----------------------------")
            print("Avalable Costing Tags")
            print("-----------------------------")
            for i, tag in enumerate(tags):
                print(f"{i + 1}. {tag}")

            key = o7util.input.input_multi('Option -> Back(b) Select(int): ')

            if isinstance(key, str) and key.lower() == 'b':
                return None

            if isinstance(key, int) and  0 < key <= len(tags):
                return tags[key - 1]

    #*************************************************
    #
    #*************************************************
    def menu_dimension(self) -> str:
        """Return a selected dimension"""

        dimensions =[
            'AZ',
            'INSTANCE_TYPE',
            'LINKED_ACCOUNT',
            'OPERATION',
            'PURCHASE_TYPE',
            'SERVICE',
            'USAGE_TYPE',
            'PLATFORM',
            'TENANCY',
            'RECORD_TYPE',
            'LEGAL_ENTITY_NAME',
            'INVOICING_ENTITY',
            'DEPLOYMENT_OPTION',
            'DATABASE_ENGINE',
            'CACHE_ENGINE',
            'INSTANCE_TYPE_FAMILY',
            'REGION',
            'BILLING_ENTITY',
            'RESERVATION_ID',
            'SAVINGS_PLANS_TYPE',
            'SAVINGS_PLAN_ARN',
            'OPERATING_SYSTEM'
        ]

        while True :

            self.console_title(left='Avalable Costing Dimensions')
            print("Avalable Costing Dimensions")
            for i, dimension in enumerate(dimensions):
                print(f"{i + 1}. {dimension}")

            key = o7util.input.input_multi('Option -> Back(b) Select(int): ')

            if isinstance(key, str) and key.lower() == 'b':
                return None

            if isinstance(key, int) and  0 < key <= len(dimensions):
                return dimensions[key - 1]

    #*************************************************
    #
    #*************************************************
    def menu_account(self) -> str:
        """Return a selected tag"""

        accounts = self.load_accounts()

        while True :

            self.console_title(left='Linked Account List')
            print(accounts[['Id','Name','Email','Status']])
            key = o7util.input.input_multi('Option -> Back(b) Select(int): ')

            if isinstance(key, str) and key.lower() == 'b':
                return None

            if isinstance(key, int) and  0 <= key < len(accounts.index):
                return accounts.iloc[key]['Id']



    #*************************************************
    #
    #*************************************************
    def menu(self):
        """Menu"""
        self.group_type ='DIMENSION'
        self.group_key  = 'LINKED_ACCOUNT'
        self.filters = []

        show_raw = False


        self.update_costs()

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', o7t.get_width())
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.float_format', '{:,.2f}'.format)  # https://docs.python.org/2/library/string.html#formatstrings

        while True :

            if show_raw:
                df_costs_with_sum = self.df_costs.copy()
                df_costs_with_sum.loc['Total'] = self.df_costs.sum()
                self.display_daily(df_costs_with_sum)
            else :
                self.display_daily(self.df_costs_summarize)

            key = o7util.input.input_multi(
                'Option -> Back(b), View(v) by Tag(t), by Account(a), by Usage(u), by Dimension(d), To Excel(x), Reset(r), Filter(int): '
            )

            if isinstance(key, str):
                key=key.lower()

                if key == 'b':
                    break

                if key == 'v':
                    show_raw = not show_raw

                if key == 't':
                    self.group_type = 'TAG'
                    self.group_key = self.menu_tag()
                    self.update_costs()

                if key== 'a':
                    self.group_type ='DIMENSION'
                    self.group_key  = 'LINKED_ACCOUNT'
                    self.update_costs()

                if key == 'u':
                    self.group_type ='DIMENSION'
                    self.group_key  = 'USAGE_TYPE'
                    self.update_costs()

                if key == 'd':
                    self.group_type ='DIMENSION'
                    self.group_key  = self.menu_dimension()
                    self.update_costs()

                if key == 'r':
                    self.filters = []
                    self.update_costs()


                if key == 'x':
                    filename= f"aws-cost-{datetime.datetime.now().isoformat()[0:19].replace(':','-')}.xlsx"
                    with pd.ExcelWriter(filename) as writer: # pylint: disable=abstract-class-instantiated

                        df_parameters = pd.DataFrame([
                            {'Parameter' : 'Date', 'Value' : datetime.datetime.now().isoformat()},
                            {'Parameter' : 'Group By', 'Value' : f'{self.group_type } - {self.group_key}'},
                            {'Parameter' : 'Filters', 'Value' : self.filters_str()}
                        ])

                        df_parameters.to_excel(writer, sheet_name="Parameters")
                        self.df_costs_summarize.to_excel(writer, sheet_name="Summary")
                        self.df_costs.to_excel(writer, sheet_name="Raw")
                    print(f"Cost saved in file: {filename}")
                    o7lib.util.input.WaitInput()

            if isinstance(key, int)  and not show_raw and 0 <= key < len(self.df_costs_summarize.index):

                value = self.df_costs_summarize.loc[key][self.group_key]
                print(f"Getting Detailed for value: {value}")

                if self.group_type == 'TAG' :
                    new_filter = {
                        'Tags' : {'Key' : self.group_key, 'Values' : [value], 'MatchOptions' : ['EQUALS']}
                    }
                else :
                    new_filter = {
                        'Dimensions' : {'Key' : self.group_key, 'Values' : [value], 'MatchOptions' : ['EQUALS']}
                    }

                self.filters.append(new_filter)
                self.update_costs()

                o7util.input.wait_input()


#*************************************************
#
#*************************************************
def menu(**kwargs):
    """Run Conformity Report"""
    CostExplorer(**kwargs).menu()


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    the_ce = CostExplorer()
    CostExplorer().menu()

    # the_costs = the_ce.get_cost()
    # print(the_costs)

    # CostExplorer().conformity_report()
    # print(f'List of tags: {the_ce.list_tags()}')

    # the_accounts = the_ce.load_accounts()

    # print(the_accounts[['Id', 'Name', 'Status', 'Email']])
    #costs = the_ce.load_costs(tag_key='Project'
