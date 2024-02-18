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
from typing import List


#*************************************************
#
#*************************************************
class BgColors: #pylint: disable=too-few-public-methods
    """ Color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Constant: # pylint: disable=too-few-public-methods
    """ Constant values for report"""
    line = '-' * 40
    bigline = '#' * 40




@dataclasses.dataclass
class Parameter: # pylint: disable=too-many-instance-attributes
    """Report Parameter"""
    name        : str
    value       : str  = ""

@dataclasses.dataclass
class Test: # pylint: disable=too-many-instance-attributes
    """Section of a Report"""
    name        : str
    passed      : bool  = False
    critical    : bool  = True
    reason      : str   = None

@dataclasses.dataclass
class Section: # pylint: disable=too-many-instance-attributes
    """Section of a Report"""
    name        : str
    tests       : List[Test] = None
    passed      : int = 0
    failed      : int = 0
    warning     : int = 0

    def __post_init__(self):
        if self.tests is None:
            self.tests = []

#*************************************************
#
#*************************************************
class Report:
    """ Class to manage report"""

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def __init__(self, name="", section_name=None, printout = True):

        self.name = name
        self.sections : list[Section]= []
        self.parameters : list[Parameter] = []
        self.active_section = -1
        self.in_progress : Test = None
        self.printout = printout

        if self.printout:
            self.print_report_header()

        if section_name is not None :
            self.add_section(name=section_name)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def add_section(self, name=""):
        """ Add a section to the report"""

        if self.in_progress is not None:
            self.test_fail()

        entry = Section(name=name)
        self.sections.append(entry)
        self.active_section = len(self.sections) - 1

        if self.printout:
            if self.active_section > 0:
                self.print_section_footer(self.sections[self.active_section - 1])

            self.print_section_head(entry)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def add_result(self, test : Test):
        """ Add a result to the report"""

        if self.active_section < 0 :
            self.add_section()

        self.sections[self.active_section].tests.append(test)

        if test.passed :
            self.sections[self.active_section].passed += 1
        elif test.critical :
            self.sections[self.active_section].failed += 1
        else:
            self.sections[self.active_section].warning += 1

        if self.printout:
            self.print_test(test)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def add_parameter(self, name="", value=None):
        """ Add a parameter to the report"""

        param = Parameter (name = name, value = value)
        self.parameters.append(param)
        if self.printout:
            self.print_parameter(param)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def add_test(self, name="", critical= True):
        """ Add a test to the report"""

        if self.in_progress is not None:
            self.test_fail()
        self.in_progress = Test(name=name, critical=critical)

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def test_pass(self, reason = None):
        """ Indication that the test passed"""

        if self.in_progress is None:
            return

        self.in_progress.passed = True
        self.in_progress.reason = reason
        self.add_result(test = self.in_progress)
        self.in_progress = None

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def test_fail(self, reason = None):
        """ Indication that the test failed"""

        if self.in_progress is None:
            return

        self.in_progress.passed = False
        self.in_progress.reason = reason
        self.add_result(test = self.in_progress)
        self.in_progress = None

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def complete(self):
        """ Complete the report"""

        if self.in_progress is not None:
            self.test_fail()

        if self.printout:
            if self.active_section >= 0:
                self.print_section_footer(self.sections[self.active_section])
            self.print_summary_report()

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_section_head(self, section : Section):
        """ Print a section header"""


        print(f"{BgColors.HEADER}{Constant.line}{BgColors.ENDC}")
        print(f"{BgColors.HEADER}Section : {section.name}{BgColors.ENDC}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_section_footer(self, section : Section):
        """ Print a section footer"""

        #print(f"{BgColors.HEADER}{Constant.line}{BgColors.ENDC}")
        pct = section.passed / len(section.tests) * 100 if len(section.tests) > 0 else 0.0
        txt = f"{section.passed} / {len(section.tests)} ({pct:.2f} %)"
        print(f"{BgColors.HEADER}{section.name} Summary:{BgColors.ENDC} {txt} ")


    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_report_header(self):
        """ Print a report header"""

        print(f"{BgColors.OKCYAN}{Constant.bigline}")
        print(f"    {self.name}")
        print(f"{Constant.bigline}{BgColors.ENDC}")


    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_summary_report(self):
        """ Print a summary report"""

        print(f"{BgColors.OKCYAN}{Constant.bigline}")
        print("Report Summary")
        print(f"{Constant.bigline}{BgColors.ENDC}")

        passed = sum(section.passed for section in self.sections)
        warning = sum(section.warning for section in self.sections)
        failed = sum(section.failed for section in self.sections)
        total = sum(len(section.tests) for section in self.sections)

        print(f"  Pass    : {passed}")
        print(f"  Warning : {warning}")
        print(f"  Fail    : {failed}")
        print(f"  TOTAL   : {total}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_test(self, test : Test):
        """ Print a test result"""

        txt = f"{test.name}: {test.reason}" if test.reason is not None else test.name

        if test.passed :
            print(f"[{BgColors.OKGREEN}PASS{BgColors.ENDC}] {txt}")
        elif test.critical :
            print(f"[{BgColors.FAIL}ERR!{BgColors.ENDC}] {txt}")
        else:
            print(f"[{BgColors.WARNING}WARN{BgColors.ENDC}] {txt}")

    #---------------------------------------------------------------------------------------------
    #
    #---------------------------------------------------------------------------------------------
    def print_parameter(self, parameter : Parameter):
        """ Print a parameter"""

        txt = f"{parameter.name}: {parameter.value}" if parameter.value is not None else parameter.name
        print(f"{txt}")

#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    r = Report('TheReport', section_name="First Section")
    assert r.name == 'TheReport'
    assert len(r.sections) == 1
    assert len(r.sections[0].tests) == 0
    assert r.sections[0].name == "First Section"

    r.add_result(Test(name="Test OK", passed=True, critical=True))
    assert len(r.sections[0].tests) == 1
    assert r.sections[0].passed == 1

    r.add_result(Test(name="Test Fail", reason="Funny Stuff", passed=False, critical=True))
    assert len(r.sections[0].tests) == 2
    assert r.sections[0].failed== 1

    r.add_result(Test(name="Test Fail but not critical", passed=False, critical=False))
    assert len(r.sections[0].tests) == 3
    assert r.sections[0].warning == 1

    r.add_section("Second Section")
    assert len(r.sections) == 2
    assert len(r.sections[1].tests) == 0

    assert r.in_progress is None
    r.add_test("Step by Step Test 1", False)
    assert r.in_progress is not None
    assert r.in_progress.critical is False

    r.test_pass()
    assert r.in_progress is None
    assert len(r.sections[1].tests) == 1

    r.add_test("Step by Step Test 2", True)
    assert r.in_progress is not None
    assert r.in_progress.critical is True

    r.test_fail("Wrong Id")
    assert r.in_progress is None
    assert len(r.sections[1].tests) == 2


    r.add_test("Step by Step Test 3", False)
    assert r.in_progress is not None
    assert r.in_progress.critical is False


    r.complete()
    assert len(r.sections[1].tests) == 3
