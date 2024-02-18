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

"""Package to explores files & directories """

import os
import pathlib
#import pprint
import o7util.input as o7i
import o7util.table as o7tbl



#*************************************************
#
#*************************************************
class FileExplorer():

    """Class to explore files & directories"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, cwd : str = '.'):

        self.cwd = os.path.realpath(cwd)


    #*************************************************
    #
    #*************************************************
    def scan_directory(self, filters = None) -> list[dict]:

        """List all files in the current directory """
        files = []

        # https://docs.python.org/3/library/os.html#os.scandir
        with os.scandir(path = self.cwd) as entries:
            for entry in entries:

                # https://docs.python.org/3/library/os.html#os.stat_result
                stats = entry.stat()
                #print(f'{entry.name} - stats: {stats}')

                ftype = ''
                size = stats.st_size
                extention = None
                if entry.is_dir():
                    ftype += 'd'
                    size = None
                if entry.is_file():
                    ftype += 'f'
                    extention = pathlib.Path(entry.path).suffix
                # if entry.is_symlink():
                #     ftype += 's'

                if filters is not None and 'extensions' in filters:
                    if entry.is_file() and (extention not in filters['extensions']):
                        continue

                files.append({
                    'name': entry.name,
                    'path' : entry.path,
                    'type' : ftype,
                    'size' : size,
                    'extention': extention,
                    #'created': stats.st_birthtime,
                    'updated' : stats.st_mtime
                })

        # Sort list
        files.sort(key=lambda x: x.get('type') + x.get('name'))


        return files

    #*************************************************
    #
    #*************************************************
    def diplay_directory(self, filters = None):
        """Display the Current Directory"""

        files = self.scan_directory(filters = filters)

        #diskUsage = shutil.disk_usage(self.cwd)
        # print('Disk Usage')
        # pprint.pprint(diskUsage)

        params = o7tbl.TableParam(
            title = f'Active Directory: {self.cwd}',
            columns = [
                o7tbl.ColumnParam(title = 'id'          , type = 'i',       min_width= 4  ),
                o7tbl.ColumnParam(title = 'Type'        , type = 'str',     data_col = 'type'),
                o7tbl.ColumnParam(title = 'Name'        , type = 'str',     data_col = 'name'),
                o7tbl.ColumnParam(title = 'Size'        , type = 'bytes',   data_col = 'size'),
                o7tbl.ColumnParam(title = 'Extension'   , type = 'str',     data_col = 'extention'),
                o7tbl.ColumnParam(title = 'Updated'     , type = 'since',   data_col = 'updated')
            ]
        )
        o7tbl.Table(params, files).print()

        return files

    #*************************************************
    #
    #*************************************************
    def select_file(self, filters = None):
        """Select a file in the current directory"""

        while True :
            files = self.diplay_directory(filters = filters)

            key = o7i.input_multi('Option -> Back(b) Parent(p) Remove Filters (r) Select File (int): ')

            if isinstance(key, str):
                if key.lower() == 'b':
                    return None

                if key.lower() == 'p':
                    self.cwd = pathlib.Path(self.cwd).parent

                if key.lower() == 'r':
                    filters= None

            if isinstance(key, int) and (0 < key <= len(files)):
                print(f'Selected File : {files[key - 1]["path"]}')
                file = files[key - 1]
                if file["type"] == 'd':
                    self.cwd = file['path']
                else:
                    return file['path']


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":


    theFE = FileExplorer(cwd = '.')
    theFE.select_file()
