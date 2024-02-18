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

"""Package to display array in a table format (console, HTML...) """

import datetime
import dataclasses
from typing import Any

import o7util.search
import o7util.format
import o7util.conversion
import o7util.terminal as o7t

# RefS
# Charaters for boxes: https://en.wikipedia.org/wiki/Box-drawing_character#Box_Drawing


@dataclasses.dataclass
class ColumnParam: # pylint: disable=too-many-instance-attributes
    """Parameters for a column"""
    title       : str = ''
    type        : str = '' # (str, int, float, date, datetime, since, bytes, percent, i)
    data_col    : str = 'not-set'

    width       : int = None # Width of the column
    max_width   : int = None # Maximum Width for a column
    min_width   : int = None # Minimum Width for a column
    fix_width   : int = None # Column is for a to a specific width
    data_width  : int = 0
    term_width  : int = 0

    footer      : str = None  # Footer for the column (sum, avg, max, min, count)
    group       : str = None  # Header grouping (groups header with same value)

    alarm       : Any = None  # Value equal to for alarm format
    normal      : Any = None  # Value equal to for normal format
    critical_hi : float = None  # Critical when Value is equal or above
    alarm_hi    : float = None  # Alarm when Value is equal or above
    alarm_lo    : float = None  # Alarm when Value is equal or below
    warning_hi  : float = None  # Warning when Value is above or below
    warning_lo  : float = None  # Warning when Value is equal or below
    low_hi      : float = None       # Low when Value is equal or above
    sort        : str = None   # (asc or des) If the data should be sort on this columns
    format      : str = None    # Special formating for this column, options
                                    # aws-status
                                    # aws-state  (EC2 States)
                                    # aws-drift
                                    # aws-edit

    def __post_init__(self):
        if self.type == 'i':
            self.data_col = 'i'
        self.width = len(self.title)

@dataclasses.dataclass
class TableParam: # pylint: disable=too-many-instance-attributes
    """Parameters for a table"""
    title       : str = ''
    with_group  : bool = False
    with_header : bool = True
    with_footer : bool = True
    columns     : list[ColumnParam] = None

@dataclasses.dataclass
class Data: # pylint: disable=too-many-instance-attributes
    """Data values for a cell"""
    column_param    : ColumnParam
    raw             : Any
    eng             : Any = None
    is_critical     : bool = False
    is_alarm        : bool = False
    is_warning      : bool = False
    is_low          : bool = False
    is_normal       : bool = False
    txt             : str = None
    index           : int = 0


    def set_eng(self) :
        """ Set the engineering value of the data"""
        if self.column_param.type == 'since':
            self.eng = o7util.conversion.to_elapse_senconds(self.raw)
        elif self.column_param.type == 'int':
            self.eng = o7util.conversion.to_int(self.raw)
        elif self.column_param.type == 'float':
            self.eng = o7util.conversion.to_float(self.raw)
        else:
            self.eng = self.raw


    def set_state(self) :
        """Set the state of the data"""
        if self.eng is not None:

            if self.column_param.alarm is not None:
                self.is_alarm = self.column_param.alarm  == self.eng

            if self.column_param.normal is not None:
                self.is_normal = self.column_param.normal  == self.eng

            if self.column_param.critical_hi is not None:
                self.is_critical = self.eng >= self.column_param.critical_hi

            if self.column_param.alarm_hi is not None:
                self.is_alarm = self.eng >= self.column_param.alarm_hi

            if self.column_param.alarm_lo is not None:
                self.is_alarm = self.eng <= self.column_param.alarm_lo

            if self.column_param.warning_hi is not None:
                self.is_warning = self.eng > self.column_param.warning_hi

            if self.column_param.warning_lo is not None:
                self.is_warning = self.eng < self.column_param.warning_lo

            if self.column_param.low_hi is not None:
                self.is_low = self.eng > self.column_param.low_hi

    def set_txt(self) :
        """ Set the text value of the data"""
        if self.column_param.type == 'i':
            self.txt = str(self.index)
        elif self.column_param.type is None:
            self.txt = ''
        elif self.column_param.type == 'date':
            self.txt = o7util.format.to_datetime(self.eng, '%Y-%m-%d')
        elif self.column_param.type == 'datetime':
            self.txt = o7util.format.to_datetime(self.eng, '%Y-%m-%d %H:%M:%S')
        elif self.column_param.type == 'since':
            self.txt = o7util.format.elapse_time(self.eng)
        elif self.column_param.type == 'bytes':
            self.txt = o7util.format.to_bytes(self.eng)
        elif self.column_param.type == 'percent':
            self.txt = o7util.format.to_percent(self.eng, 1)
        else:
            self.txt = str(self.eng)

        self.txt = self.txt.replace('\n', ' ')



    def get_terminal_txt(self) -> str:
        """ Get the text value of the data for the terminal"""

        txt = self.txt
        txt = txt[0:self.column_param.term_width].ljust(self.column_param.term_width, ' ')

        if self.is_alarm is True or self.is_critical is True:
            txt = o7t.format_alarm(txt)
        elif self.is_warning is True or self.is_low is True :
            txt = o7t.format_warning(txt)
        elif self.is_normal is True:
            txt = o7t.format_normal(txt)
        elif self.column_param.format == 'aws-status':
            txt = o7t.format_aws_status(txt)
        elif self.column_param.format == 'aws-drift':
            txt = o7t.format_aws_drift(txt)
        elif self.column_param.format == 'aws-edit':
            txt = o7t.format_aws_edit(txt)
        elif self.column_param.format == 'aws-state':
            txt = o7t.format_aws_state(txt)

        return txt

    def get_html_txt(self) -> tuple[str, str]:
        """ Get the text value of the data for a HTML table"""

        txt = self.txt
        style = ''
        if self.is_critical is True:
            style = 'background-color: rgb(125, 33, 5); color: rgb(255, 255, 255);'
        elif self.is_alarm is True:
            style = 'background-color: rgb(186, 46, 15); color: rgb(255, 255, 255);'
        elif self.is_warning is True:
            style = 'background-color: rgb(204, 95, 33); color: rgb(255, 255, 255);'
        elif self.is_low is True:
            style = 'background-color: rgb(180, 145, 22); color: rgb(255, 255, 255);'
        elif self.is_normal is True:
            style = 'background-color: rgb(0, 0, 0);'

        return txt, style




    def __post_init__(self):
        """ Convert raw value to eng value and verify if in a special state (alarm, warning, normal)"""

        # Convert Eng Value, when required
        self.set_eng()

        # Verify if in a special state (alarm, warning, normal)
        self.set_state()

        # Reformat Value
        self.set_txt()

#*************************************************
#
#*************************************************
class Table():
    """Class to display array in a table format (console, HTML...)"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, param : TableParam = None, datas = None):

        self.param : TableParam = None

        self.raw_datas : list = []
        self.process_datas : list[dict[Data]] = None
        self.footer_datas : dict[Data] = None
        self.terminal_table_width : int = 0
        self.sorted : dict[str] = {}

        # For HTML Formatting
        self.style_border = '1px solid #999'
        self.style_td = f'border: {self.style_border}; text-align: center; font-size: 10px;'
        self.style_th = f'border: {self.style_border}; text-align: center; font-size: 10px;'

        if param is not None:
            self.configure(param)

        if datas is not None:
            self.update_data(datas)


    #*************************************************
    #
    #*************************************************
    def configure(self, param : TableParam):
        """Configure the table with provided parameters"""

        self.param = param
        self.process_datas = None
        self.sorted = {}

        #----------------------------
        # Set Sorting dictionary
        #----------------------------
        for column in self.param.columns :
            if column.sort is not None:
                self.sorted[column.data_col] = column.sort



    #*************************************************
    #
    #*************************************************
    def update_data(self, datas):
        """Update the Raw Data"""

        self.raw_datas = datas
        self.process_datas = None

        for column, order in self.sorted.items():
            self.raw_datas = sorted(
                self.raw_datas,
                key=lambda x: x[column],
                reverse=(order == 'des')
            )

    #*************************************************
    #
    #*************************************************
    def process_data(self):
        """Analyse raw data and prepare dtata for output"""

        # prepare array to receive the process data
        self.process_datas = list({} for i in range(len(self.raw_datas)))
        self.footer_datas = {}

        self.terminal_table_width = 0
        console_width = o7t.get_width()

        for column in self.param.columns :
            column.data_width = 0
            footer_data = 0.0
            footer_data_count = 0


            for i, data in enumerate(self.raw_datas):

                # Get and Transform data
                index = i + 1

                # Get value with support of "." enumeration
                raw_value = o7util.search.value_in_dict(column.data_col, data)

                self.process_datas[i][column.data_col] = Data(
                    raw=raw_value,
                    column_param=column,
                    index=index
                )

                column.data_width = max(column.data_width, len(self.process_datas[i][column.data_col].txt))

                # Calculate footer data
                if column.footer is not None:
                    if column.footer == 'sum':
                        footer_data += self.process_datas[i][column.data_col].eng
                    elif column.footer == 'avg':
                        footer_data = footer_data * footer_data_count
                        footer_data += self.process_datas[i][column.data_col].eng
                        footer_data_count += 1
                        footer_data = footer_data / footer_data_count

                    elif column.footer == 'max':
                        footer_data = max(footer_data, self.process_datas[i][column.data_col].eng)
                    elif column.footer == 'min':
                        footer_data = min(footer_data, self.process_datas[i][column.data_col].eng)
                    elif column.footer == 'count':
                        footer_data += 1

            if column.footer is not None:
                self.footer_datas[column.data_col] = Data(raw=footer_data, column_param=column, index=0)
                column.data_width = max(column.data_width, len(self.footer_datas[column.data_col].txt))


            #----------------
            # Calculate the appropriate column width
            #----------------
            column.width = max(column.width, column.data_width)

            if column.max_width is not None:
                column.width = min(column.width,  column.max_width)
            if column.min_width is not None:
                column.width = max(column.width, column.min_width)
            if column.fix_width is not None:
                column.width = column.fix_width

            #----------------
            # Calculate the column width in a temrinal windows
            #----------------
            # make sure we dont overflow terminal
            width_left =  console_width - (self.terminal_table_width + 3)
            if width_left <= 3:
                column.term_width = 0
            else:
                column.term_width = min(column.width,width_left)
                self.terminal_table_width += column.term_width + 3


    #*************************************************
    #
    #*************************************************
    def print_group(self):
        """Print Group Hearder in temrminal"""

        if self.param.with_group is False:
            return

        group_row = ''
        current_group = None
        current_group_width = 0
        for column in self.param.columns :

            if  column.term_width < 1:
                continue

            if column.group == current_group and column.group is not None:
                current_group_width += column.term_width + 3

            else:
                if current_group_width > 0:
                    group = current_group if current_group is not None else ' '
                    group = group.center(current_group_width, ' ')
                    group_row += f" {group} \U00002502"

                current_group = column.group
                current_group_width = column.term_width


        group = current_group if current_group is not None else ' '
        group = group.center(current_group_width, ' ')
        group_row += f" {group} \U00002502"


        o7t.print_header(group_row)

    #*************************************************
    #
    #*************************************************
    def print_header(self):

        """Print Table Header to console"""
        if self.param.with_header is False:
            return

        #----------------------------
        # Loop to build top tow
        #----------------------------
        top_row = ''
        for column in self.param.columns :
            if column.term_width < 1:
                continue
            title = column.title[0:column.term_width]
            title = title.center(column.term_width, ' ')
            top_row += f" {title} \U00002502"


        o7t.print_header(top_row)


    #*************************************************
    #
    #*************************************************
    def print_rows(self):
        """Print all data row in temrminal"""

        for row in self.process_datas:

            data_row = ''
            for column in self.param.columns :

                if  column.term_width < 1:
                    continue

                data : Data = row[column.data_col]
                txt = data.get_terminal_txt()
                data_row += f" {txt} \U00002502"

            print(data_row)

    #*************************************************
    #
    #*************************************************
    def print_footer(self):
        """Print Footer in temrminal"""

        if self.param.with_footer is False:
            return

        bottom_row = ''
        for column in self.param.columns :
            if  column.term_width < 1:
                continue

            if column.data_col in self.footer_datas:
                data : Data = self.footer_datas[column.data_col]
                txt = data.get_terminal_txt()
                bottom_row += f" {txt} \U00002502"

            else:
                bottom_row += f" {' ' * column.term_width} \U00002502"


        #print(bottom_row)
        # bottom_row = " " * self.terminal_table_width

        o7t.print_header(bottom_row)

    #*************************************************
    #
    #*************************************************
    def print(self, datas = None):
        """Print Table to console"""

        if datas is not None:
            self.update_data(datas)

        if self.process_datas is None:
            self.process_data()

        # Print Title
        if self.param.title :
            title = self.param.title.center(self.terminal_table_width, ' ')
            o7t.print_header(title)

        self.print_group()
        self.print_header()
        self.print_rows()
        self.print_footer()


    #*************************************************
    #
    #*************************************************
    def generate_html_group_header(self):
        """Generate HTML Group Header"""


        if self.param.with_footer is False:
            return ""

        ths = ""
        current_group = None
        current_group_count = 0
        for column in self.param.columns :

            if column.group == current_group and column.group is not None:
                current_group_count = current_group_count + 1
            else:
                if current_group_count >= 1:
                    current_group = current_group if current_group is not None else ' '
                    ths += f'<th style="{self.style_th}" colspan="{current_group_count}">{current_group}</th>'
                current_group = column.group
                current_group_count = 1

        current_group = current_group if current_group is not None else ' '
        ths += f'<th style="{self.style_th}" colspan="{current_group_count}">{current_group}</th>'

        return f'<tr>{ths}</tr>'


    #*************************************************
    #
    #*************************************************
    def generate_html_header(self):
        """Generate HTML Table Header"""

        ths = ""
        #----------------------------
        # Loop to build top tow
        #----------------------------
        for column in self.param.columns :
            title = column.title
            width = column.width * 6
            ths += f'<th style="{self.style_th} width: {width}px;">{title}</th>'

        html = f'<tr>{ths}</tr>'
        return html

    #*************************************************
    #
    #*************************************************
    def generate_html_rows(self):
        """Generate HTML Table Header"""

        html = ""
        for row in self.process_datas:
            html += '<tr>'
            for column in self.param.columns :

                data : Data = row[column.data_col]
                txt, style = data.get_html_txt()
                html += f'<td style="{self.style_td} {style}">{txt}</td>'

            html += '</tr>'


        return html

    #*************************************************
    #
    #*************************************************
    def generate_html_footers(self):
        """Generate HTML Table Header"""

        html = ""

        if self.param.with_footer is False:
            return html

        html += '<tr>'
        for column in self.param.columns :

            if column.data_col in self.footer_datas:
                data : Data = self.footer_datas[column.data_col]
                txt, style = data.get_html_txt()
                html += f'<th style="{self.style_td} {style}">{txt}</th>'
            else:
                html += '<th></th>'

        html += '</tr>'


        return html

    #*************************************************
    #
    #*************************************************
    def generate_html(self, datas = None):
        """Generate HTML Table"""

        html = f'<table style="border-collapse: collapse; border: {self.style_border}">'

        if datas is not None:
            self.update_data(datas)

        if self.process_datas is None:
            self.process_data()

        html += self.generate_html_group_header()
        html += self.generate_html_header()
        html += self.generate_html_rows()
        html += self.generate_html_footers()
        html += '</table>'

        return html


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    import pprint


    theParams = TableParam(
        title = "Cloudformation Stacks for region: ca-central-1",
        columns = [
            ColumnParam(title = 'id', type = 'i'),
            ColumnParam(title = 'Name'      , type = 'str',     min_width = 40, data_col = 'StackName'),
            ColumnParam(title = 'Creation'  , type = 'date',    max_width = 10, data_col = 'CreationTime', format = '%Y-%m-%d'),
            ColumnParam(title = 'Updated'   , type = 'since',   data_col = 'UpdateTime'),
            ColumnParam(title = 'Status'    , type = 'str',     fix_width = 15, data_col = 'StackStatus', format = 'aws-status'),
            ColumnParam(title = 'Alert'     , type = 'str',     data_col = 'Alert', alarm = True, normal = False)
            ]
    )
    theDatas = [
        {'StackName' : 'first-stack', 'CreationTime': datetime.datetime(2021, 8, 23),
        'UpdateTime': datetime.datetime(2021, 8, 24), 'StackStatus': 'COMPLETE', 'Alert' : True
        },
        {'StackName' : 'second-stack','CreationTime': datetime.datetime(2021, 8, 23),
        'UpdateTime': datetime.datetime(2021, 10, 24),'StackStatus': 'UPDATING', 'Alert' : False
        },
    ]

    theTable = Table(param=theParams)
    theTable.update_data(datas = theDatas)
    pprint.pprint(theTable.param.columns, indent=4,sort_dicts=False)


    theTable.print()
    the_html = theTable.generate_html()
    print(the_html)

    # pprint.pprint(theTable.process_datas, indent=4,sort_dicts=False)

    #--------------------------------
    # Save to File
    #--------------------------------
    # filname = 'table_html.cache.html'
    # try:
    #     with open(filname, 'w', newline='', encoding='utf-8') as htmlfile:
    #         htmlfile.write(the_html)

    # except IOError:
    #     print(f"Count not write to: {filname}")
