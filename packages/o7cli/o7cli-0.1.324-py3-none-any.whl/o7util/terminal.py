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

"""Package for Display in Terminal Functions """
import os
import shutil
import sty

os.system("") # Fix issue with Terminal colors in windows

#*************************************************
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
# https://github.com/feluxe/sty
#*************************************************
class Colors: # pylint: disable=too-few-public-methods
    """Constant for Console Colors  """
    HEADER = sty.fg.black + sty.bg.li_grey
    RED = sty.fg.li_red
    GREEN = sty.fg.li_green
    YELLOW = sty.fg.li_yellow
    BLUE = sty.fg.blue
    MAGENTA =  sty.fg.li_magenta
    CYAN = sty.fg.li_cyan
    WHITE = sty.fg.white
    ORANGE = sty.fg(255, 150, 50)

    INPUT =  sty.fg.li_magenta
    ACTION = sty.fg(255, 150, 50)

    OK = sty.fg.li_green
    WARNING = sty.fg.li_yellow
    ERROR = sty.fg.li_red
    FAIL = sty.fg.li_red
    ALARM = sty.fg.li_red

    BOLD = sty.ef.bold
    ITALIC = sty.ef.italic
    UNDERLINE = sty.ef.italic

    ENDC = sty.rs.all
    ENDF = sty.rs.fg

#*************************************************
#
#*************************************************
def get_width():
    """Get the width of current terminal window"""
    return shutil.get_terminal_size()[0]

#*************************************************
#
#*************************************************
def get_height():
    """Get the width of current terminal window"""
    return shutil.get_terminal_size()[1]

#*************************************************
#
#*************************************************
def print_header(line):
    """Print line with header formatting"""

    line = line.replace(sty.rs.fg,sty.fg.black)
    print(f"{Colors.HEADER}{line}{Colors.ENDC}")

#*************************************************
#
#*************************************************
def print_line(char = '-', length = None):
    """Print line with header formatting"""
    if length is None:
        length = get_width()
    print(f"{char * length}")


#*************************************************
#
#*************************************************
def console_line(left = "", center = "", right = ""):
    """Display a  titles using the full console wisth"""

    line = center.center(get_width(), ' ')
    line = left + line[len(left):]
    line = line[:(len(right)*(-1))] + right if len(right) > 0 else line
    print(f"{line}")

#*************************************************
#
#*************************************************
def console_title_line(left = "", center = "", right = ""):
    """Display a  titles using the full console width"""

    title = center.center(get_width(), ' ')
    title = left + title[len(left):]
    title = title[:(len(right)*(-1))] + right if len(right) > 0 else title

    print(f"{Colors.HEADER}{title}{Colors.ENDC}")

#*************************************************
#
#*************************************************
def clear():
    """Clear Terminal Window"""
    print("\033[H\033[J", end="")

#*************************************************
#
#*************************************************
def console_title(left = "", center = "", right = ""):
    """Clear Console & add Title"""
    clear()
    console_title_line(left, center, right)

#*************************************************
#
#*************************************************
def format_alarm(val):
    """Return the value with alarm format"""
    return f"{Colors.ALARM}{val}{Colors.ENDF}"


#*************************************************
#
#*************************************************
def format_warning(val):
    """Return the value with warning format"""
    return f"{Colors.WARNING}{val}{Colors.ENDF}"

#*************************************************
#
#*************************************************
def format_normal(val):
    """Return the value with normal format"""
    return f"{Colors.OK}{val}{Colors.ENDF}"

#*************************************************
#
#*************************************************
def format_aws_status(val):
    """Return the value with the color depending on AWS Status"""
    ret = val
    val = val.upper()
    if 'FAIL' in val or 'STOP' in val or 'CANCEL' in val :
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"
    elif 'IN_PROGRESS' in val:
        ret = f"{Colors.CYAN}{ret}{Colors.ENDC}"
    elif 'COMPLETE' in val or 'SUCCE' in val or 'ACTIVE' in val  or 'RUNN' in val or 'PASS' in val or 'AVAIL' in val:
        ret = f"{Colors.OK}{ret}{Colors.ENDC}"
    elif 'SUPERSED' in val:
        ret = f"{Colors.WARNING}{ret}{Colors.ENDC}"
    elif 'PROGRESS' in val or 'PROVI' in val  or 'ACTIVAT' in val:
        ret = f"{Colors.CYAN}{ret}{Colors.ENDC}"

    return ret

#*************************************************
#
#*************************************************
def format_aws_drift(val):
    """Add color to AWS Drift status string"""
    ret = val
    if 'DRIFTED' in val:
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"
    elif 'IN_SYNC' in val:
        ret = f"{Colors.OK}{ret}{Colors.ENDC}"
    elif 'UNKNOWN' in val:
        ret = f"{Colors.CYAN}{ret}{Colors.ENDC}"
    elif 'NOT_CHECKED' in val:
        ret = f"{Colors.CYAN}{ret}{Colors.ENDC}"
    elif 'MODIFIED' in val:
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"

    return ret

#*************************************************
#
#*************************************************
def format_aws_edit(val):
    """Add color to AWS Drift status string"""
    ret = val
    if 'del' in val or 'remove' in val:
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"
    elif 'new' in val or 'add' in val:
        ret = f"{Colors.OK}{ret}{Colors.ENDC}"
    elif 'cur' in val or 'same' in val:
        ret = f"{Colors.WHITE}{ret}{Colors.ENDC}"
    elif 'mod' in val or 'change' in val:
        ret = f"{Colors.WARNING}{ret}{Colors.ENDC}"

    return f"{Colors.CYAN}{ret}{Colors.ENDC}"


#*************************************************
#
#*************************************************
def format_aws_state(val):
    """Add color to AWS Instance State string"""
    ret = val
    if 'shutting-down' in val:
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"
    elif 'running' in val:
        ret = f"{Colors.OK}{ret}{Colors.ENDC}"
    elif 'available' in val:
        ret = f"{Colors.OK}{ret}{Colors.ENDC}"
    elif 'pending' in val:
        ret = f"{Colors.CYAN}{ret}{Colors.ENDC}"
    elif 'stop' in val:
        ret = f"{Colors.FAIL}{ret}{Colors.ENDC}"

    return ret
