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
"""Package to make color conversions and operations"""
import math


#*************************************************
#
#*************************************************
def dec_to_hex(red, green, blue):
    """Convert RGB color to HEX value for HTML"""
    red = int(red * 255)
    green = int(green * 255)
    blue = int(blue * 255)
    return f'#{red:02x}{green:02x}{blue:02x}'


#*************************************************
#
#*************************************************
def scale_b_to_r_to_y(val, min_val, max_val):
    """Return Generate Scaled Color from Blue to Red to Yellow """

    # Normalize to 0-1
    try:
        ratio = float(val-min_val)/(max_val-min_val)
    except ZeroDivisionError:
        ratio = 0.5

    blue  = min((max((4*(0.75-ratio), 0.)), 1.))
    red   = min((max((4*(ratio-0.25), 0.)), 1.))
    green = min((max((4*math.fabs(ratio-0.5)-1., 0.)), 1.))
    return dec_to_hex(red, green, blue)

#*************************************************
#
#*************************************************
def scale_red_to_green(val, min_val, max_val, k = 1):
    """Return Generate Scaled Color from Red to Green """

    # Normalize to 0-1
    try:
        ratio = float(val-min_val)/(max_val-min_val)
    except ZeroDivisionError:
        ratio = 0.5

    red   = min(max(1-ratio,0.0) * 2,1.0)
    green = min(max(ratio,0.0) * 2,1.0)
    blue = min(red, green) * k
    return dec_to_hex(red, green, blue)

#*************************************************
#
#*************************************************
def scale_3_step(val, min_val, mid_val, max_val):
    """Return Generate Scaled Color from White to Green(mid value) to Red.  Used for Wind Speed"""

    ext_val = ((max_val - min_val) * 2) + min_val

    if val < min_val:
        red = green = blue = 1.
    elif val <= mid_val:
        ratio = float(val-min_val)/(mid_val-min_val)
        green = 1.
        blue = red = 1. - ratio
    elif val <= max_val:
        ratio = float(val-mid_val)/(max_val-mid_val)
        red = min(ratio * 2., 1.)
        green = min((1. - ratio) * 2, 1.)
        blue = 0.

    elif val <= ext_val:
        ratio = float(val-max_val)/(ext_val-max_val)
        red = 1.
        green = 0.
        blue = ratio

    else: red = green = blue = 0.

    return dec_to_hex(red, green, blue)


#*************************************************
#
#*************************************************
def color_scale_tests():
    """Generate an HTML page to test and display the Color Scaling"""


    html = '<table style="border-collapse: collapse; border: 1px solid #999">'
    style_th = 'style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px"'
    style_td = 'style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px"'


    html += f'''
    <tr>
    <th {style_th}>Value</th>
    <th {style_th}>ScaleBtoRtoY</th>
    <th {style_th}>ScaleRedtoGreen</th>
    <th {style_th}>Scale3Step</th>
    </tr>'
    '''
    for i in range(0,100):
        row = '<tr>'
        row += f'<td {style_td}>{i}</td>'
        color_hex = scale_b_to_r_to_y(i,0,100)
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {color_hex}">{color_hex}</td>'
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {color_hex}">{color_hex}</td>'
        color_hex = scale_3_step(i,5, 15, 25)
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {color_hex}">{color_hex}</td>'

        row += '</tr>'
        html += row

    html += '</table>'
    return html

#*************************************************
#
#*************************************************
if __name__ == "__main__":


    #print(f'ColorDecToHex(1,1,1) -> {ColorDecToHex(0.5,0,0.25)}')

    theHTML = color_scale_tests()
    #--------------------------------
    # Save to File
    #--------------------------------
    FILENAME = 'colors.cache.html'
    try:
        with open(FILENAME, 'w', newline='', encoding='utf-8') as htmlfile:
            htmlfile.write(theHTML)

    except IOError:
        print(f"Count not write to: {FILENAME}")
