#!/usr/bin/env python
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

# python -m unittest tests.test_util_format

"""Package to format some values of object to string """

import datetime
import o7util.conversion as o7c


#*************************************************
#
#*************************************************
def to_datetime(value, date_format = '%Y-%m-%d %H:%M:%S'):
    """Convert a DateTime (object or unix int) into a Text Form"""

    #print(f'FormatDatetime Value Type {type(value)}')
    if value is None:
        return ''

    dt_class = o7c.to_datetime(value)
    if isinstance(dt_class, datetime.datetime) is False:
        return ''

    return dt_class.strftime(date_format)


#*************************************************
#
#*************************************************
def elapse_time(value):
    """Convert a DateTime or Seconds (int) into Text about the elapse time (ex: 6 sec, 3.2 min)"""

    # print(f'FormatSince Value Type {type(value)} {value=}')
    time_units = [
        {'txt': 'sec', 'scale' : 60.0},
        {'txt': 'min', 'scale' : 60.0},
        {'txt': 'hr', 'scale' : 24.0},
        {'txt': 'day', 'scale' : 365.0},
        {'txt': 'yr', 'scale' : 1.0}
    ]

    if value is None:
        return ''

    since = o7c.to_elapse_senconds(value)
    unit = 'NA'

    if since is None:
        return unit

    # Convert and fine unit
    for time_unit in time_units:
        unit = time_unit['txt']
        if since < time_unit['scale']:
            break
        since = since / time_unit['scale']

    return f'{since:.1f} {unit}'

#*************************************************
#
#*************************************************
def to_bytes(value):
    """Convert a Byte Value into Text (ex: 16 B, 345 MB)"""

    # print(f'FormatSince Value Type {type(value)} {value=}')
    byte_units = [
        {'txt': 'B', 'scale' : 1024},
        {'txt': 'KB', 'scale' : 1024},
        {'txt': 'MB', 'scale' : 1024},
        {'txt': 'GB', 'scale' : 1024},
        {'txt': 'TB', 'scale' : 1024},
        {'txt': 'PB', 'scale' : 1}
    ]

    if value is None:
        return ''

    bytes_value = float(value)
    unit = 'NA'

    # Convert and fine unit
    for byte_unit in byte_units:
        unit = byte_unit['txt']
        if bytes_value < byte_unit['scale']:
            break
        bytes_value = bytes_value / byte_unit['scale']

    return f'{bytes_value:.1f} {unit}'

#*************************************************
#
#*************************************************
def to_percent(value, decimals = 1):
    """Convert numeric value to percent"""

    if value is None:
        return ''

    # IF value is numeric
    if not isinstance(value, (int, float)) :
        return value

    return f'{value * 100:.{decimals}f} %'
