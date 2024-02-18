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
""" Report module"""

import dataclasses

@dataclasses.dataclass
class Section: # pylint: disable=too-many-instance-attributes
    """Section of a Report"""
    title   : str = ""
    html    : str = ""


#*************************************************
#
#*************************************************
class HtmlReport:
    """ Class genrating an HTML report; typically used to send by e-mail"""

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def __init__(self, name=""):

        self.name = name
        self.sections : list[Section]= []

        self.style_title =  "style='font-size: 14px; font-weight: bold;'"
        self.style_section = "style='background-color: #f0f0f0; padding: 5px 5px 5px 10px;'"

        self.greeting = "Bon Matin Capitaine"
        self.goodbye = "Bonne Journée !"

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def add_section(self, **kwargs):
        """ Add a section to the report"""
        self.sections.append(Section(**kwargs))
        return self

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def generate(self):
        """ Generate the HTML report"""

        html = f'''<!DOCTYPE html><html><body>
        <div lang=EN-US style='font-family: "Montserrat", Sans-serif; font-size: 12px; color: #485061; background-color: #ffffff'>
        {self.greeting},<br>
        <br>
        '''

        for section in self.sections :

            section_html = ""
            if section.title != "":
                section_html += f"<span {self.style_title}>{section.title}</span><br>"
            if section.html != "":
                section_html += f"<div {self.style_section}>{section.html}</div><br>"

            html = html + section_html

        html = html + f'''
        {self.goodbye}
        </div></body></html>
        '''

        return html



#*************************************************
# To Test Class
#****************************
if __name__ == "__main__":

    the_obj = HtmlReport()
    the_html = the_obj.generate()

    print('*'*80)
    print(the_html)
    print('*'*80)

