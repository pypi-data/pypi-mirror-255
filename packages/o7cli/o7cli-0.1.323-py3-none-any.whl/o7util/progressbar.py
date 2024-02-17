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

""" Progress Bar Class"""
import sys


class ProgressBar: # pylint: disable=too-few-public-methods
    """Class to display a progress bar"""
    def __init__(self, size=25, total=100):
        self.size = size
        self.progress = -1
        self.total = total
        self.current=0
        self.step=self.total / self.size
        self.form="[%-" + str(self.size) + "s] %i of %i"


    def kick(self, inc=1):
        """increase progress bar by inc"""
        self.current += inc
        percent = int(self.current / self.step)
        if percent == self.progress:
            return

        self.progress = percent
        sys.stdout.write('\r')
        sys.stdout.write(self.form % ('='*self.progress, self.current, self.total))
        sys.stdout.flush()


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    import time

    obj = ProgressBar()
    for i in range(0, 100):
        obj.kick()
        time.sleep(0.01)
