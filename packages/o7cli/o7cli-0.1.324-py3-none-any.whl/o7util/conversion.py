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
""" Package for value conversion """
import math
import datetime

# python -m unittest tests.test_util_conversion

#*************************************************
#
#*************************************************
def speed_uv_to_ws(u,v): # pylint: disable=invalid-name
    """ Convert u,v vector to speed """
    return math.sqrt( (u ** 2) + (v ** 2) )



#*************************************************
#
#*************************************************
def speed_ms_to_knot(ms): # pylint: disable=invalid-name
    """ Convert meter/sec to Knots """
    return ms * 1.944


#*************************************************
#
#*************************************************
def direction_uv_to_deg(u,v): # pylint: disable=invalid-name
    """ Convert u,v vector to direction in degree """
    rad = math.atan2(u * -1., v * -1.)
    deg = (rad * 180.) / math.pi
    if deg < 0 :
        deg += 360.0

    return deg


#*************************************************
#
#*************************************************
def direction_deg_to_txt(deg : float):
    """ Convert direction in degree to text """

    if math.isnan(deg):
        return ''

    txt = [ 'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
    i = round((deg / 360) * 16)
    if i >= 16:
        i = 0
    return txt[i]


#*************************************************
#
#*************************************************
def to_datetime(value):
    """Convert possible int or float to datetime"""

    if isinstance(value, (int, float)) is False:
        return value

    if value >= 1000000000000:
        return datetime.datetime.fromtimestamp(value/1000)

    if value >= 1000000000:
        return datetime.datetime.fromtimestamp(value)

    return value

#*************************************************
#
#*************************************************
def to_elapse_senconds(value):
    """Convert input to return the elapse time in second"""

    elapse = None
    value = to_datetime(value)

    if isinstance(value, int):
        elapse = value
    elif isinstance(value, float):
        elapse = value
    elif isinstance(value, str):
        elapse = float(value)
    elif isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            delta = datetime.datetime.utcnow() - value
        else:
            delta = datetime.datetime.now(datetime.timezone.utc) - value
        elapse = delta.total_seconds()
    elif isinstance(value, datetime.timedelta):
        elapse = value.total_seconds()
    else:
        return None

    return float(elapse)


#*************************************************
#
#*************************************************
def to_int(value):
    """Convert input to int"""
    if value is None:
        return None

    try:
        ret=int(value)
    except ValueError:
        return None

    return ret

#*************************************************
#
#*************************************************
def to_float(value):
    """Convert input to int"""
    if value is None:
        return None

    try:
        ret=float(value)
    except ValueError:
        return None

    return ret

#*************************************************
#
#*************************************************
if __name__ == "__main__":


    for d in range(0,360):
        print(f'{d} -> {direction_deg_to_txt(d)}')
