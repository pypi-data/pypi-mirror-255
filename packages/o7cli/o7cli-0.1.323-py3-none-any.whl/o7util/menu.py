"""Console Menu Package"""
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

import traceback
import dataclasses
import datetime
from typing import Callable


import o7util.input as o7i
import o7util.terminal as o7t

@dataclasses.dataclass
class Option: # pylint: disable=too-many-instance-attributes
    """Class for a menu option"""
    key : str = None
    name : str = ""
    short : str = None
    callback : Callable = None
    wait : bool = True

    def __post_init__(self):
        if self.short is None:
            self.short = self.name

#*************************************************
#
#*************************************************
class Menu():
    """Class for menu management"""

    #*************************************************
    #
    #*************************************************
    def __init__(self,
            title : str = None,
            exit_option : str = 'b',
            compact : bool = False,
            title_extra : str = "",
            display_callback : Callable = None
        ):

        self.options : dict[Option] = {}
        self.title : str = title
        self.title_extra : str = title_extra
        self.exit_option : str = exit_option
        self.compact : bool = compact
        self.display_callback : Callable = display_callback


    #*************************************************
    #
    #*************************************************
    def add_option(self, option : Option):
        """add a menu option"""
        self.options[option.key] = option

    #*************************************************
    #
    #*************************************************
    def display_title(self):
        """Display the title"""

        if self.title is not None:
            center = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%Sz')
            o7t.console_title(left =self.title, center=center, right=self.title_extra)

    #*************************************************
    #
    #*************************************************
    def display_options(self):
        """Display the options"""

        question = 'Select Option :'

        if self.compact:
            str_options = [ f"{option.short}({key})" for key, option in self.options.items()    ]
            question = f"Options -> Back({self.exit_option}) {' '.join(str_options)}:"

        else:
            o7t.print_line()
            for key, option in self.options.items():
                print(f"({key}) {option.name}")

            print(f"({self.exit_option}) Go back")

        return o7i.input_multi(question)


    #*************************************************
    #
    #*************************************************
    def process_input(self, key: str or int):
        """Display the page content"""

        if isinstance(key, int) and 'int' in self.options:
            self.options['int'].callback(key)
            return 1

        if isinstance(key, str) and key == 'int':
            print(o7t.format_alarm('Enter an integer'))
            return 2

        option = self.options.get(key, None)
        if option is None:
            return None

        option.callback()

        if option.wait:
            o7i.wait_input()

        return 1


    #*************************************************
    #
    #*************************************************
    def loop(self):
        """Display, Wait for option"""

        while True :
            try:

                self.display_title()
                if self.display_callback is not None:
                    self.display_callback()
                key = self.display_options()

                if key == self.exit_option:
                    break

                self.process_input(key)

            except KeyboardInterrupt as exc:
                raise exc

            except Exception as exc: # pylint: disable=broad-except
                print(f"Uncaught Exception -> {exc}")
                traceback.print_exc()
                o7i.wait_input()


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":


    the_menu = Menu(exit_option = 'x', title='Test Menu')

    the_menu.add_option(Option(key='a', name='Option A', callback=lambda: print('Option A')))
    the_menu.add_option(Option(key='b', name='Option B', callback=lambda: print('Option B')))

    the_menu.loop()

    the_menu.compact = True
    the_menu.loop()
