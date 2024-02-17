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
""" Package with function to request input from user"""
import inspect
import sys

import o7util.terminal as o7t


#*************************************************
# https://www.geeksforgeeks.org/class-as-decorator-in-python/
#*************************************************
class _InputDecorator: #pylint: disable=too-few-public-methods
    """Decorator Class to add format to Input functions"""

    def __init__(self, function, question_suffix : str = None):
        self.function = function
        self.default_question = None
        self.question_suffix = question_suffix

        signature = inspect.signature(function)
        for param in signature.parameters.values():
            #print(f'{param.name} -> default: {param.default}')
            if param.name == 'question':
                self.default_question = param.default

    def __call__(self, question = None, color = o7t.Colors.ACTION, **kwargs):

        if question is None:
            question = self.default_question

        if self.question_suffix is not None:
            question = f'{question}{self.question_suffix}'

        if color is not None:
            question = f'{color}{question}{o7t.Colors.ENDC}'

        result = self.function(question, **kwargs)

        return result


def input_decorator(function=None, question_suffix : str =None):
    """# wrap _InputDecorator to allow for deferred calling"""
    if function:
        return _InputDecorator(function)

    def wrapper(function):
        return _InputDecorator(function, question_suffix=question_suffix)
    return wrapper

#*************************************************
#
#*************************************************
def get_input(question : str):
    """Stub in front of inputs"""
    answer = input(f'{question}{o7t.Colors.INPUT}')
    sys.stdout.write(o7t.Colors.ENDC)
    return answer


#*************************************************
#
#*************************************************
@input_decorator(question_suffix = ' (y/n):')
def is_it_ok(question : str ='Is it OK'):
    """Ask a question and wait for a boolean answer"""
    while True:
        key = get_input(question)
        if key.lower()  == 'y':
            return True
        if key.lower()  == 'n':
            return False


#*************************************************
#
#*************************************************
@input_decorator
def wait_input(question : str ='Press to continue'):
    """Wait for any input to continue"""
    return get_input(question)

#*************************************************
#
#*************************************************
@input_decorator
def input_int(question : str = 'How much ?(int)'):
    """Ask and expects an integer"""

    try:
        ret=int(get_input(question))
    except ValueError:
        print("Not an integer")
        return None

    return ret

#*************************************************
#
#*************************************************
@input_decorator
def input_string(question : str = 'Enter Text'):
    """Request a Text String"""

    ret=str(input(question))
    return ret

#*************************************************
#
#*************************************************
@input_decorator
def input_multi(question : str ='Enter Text or Int :'):
    """Request a Text String or an Integer"""

    ret = None
    rx_input = get_input(question)

    try:
        ret=int(rx_input)
    except ValueError:
        ret=str(rx_input)

    return ret


#*************************************************
# To Pacakage
#*************************************************
if __name__ == "__main__":

    theVal = input_multi()
    print(theVal)
