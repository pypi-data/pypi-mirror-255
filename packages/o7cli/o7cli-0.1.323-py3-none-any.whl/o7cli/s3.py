#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
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
"""Module to manage S3 function"""

#--------------------------------
#
#--------------------------------
import pprint
import os
import logging


from o7util.table import TableParam, ColumnParam, Table
import o7util.menu as o7m
import o7util.input as o7i
import o7util.file_explorer as o7fe
import o7util.format as o7f


import o7lib.aws.base


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class S3(o7lib.aws.base.Base):
    """Class to manage S3 operations"""

    #  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.client = self.session.client('s3')

        self.buckets : list = []

        self.bucket : str = ""
        self.prefix : str = ""
        self.key    : str = ""

        self.objects : list = []
        self.s3_object : dict = {}

    #*************************************************
    #
    #*************************************************
    def load_buckets(self):
        """Load all Buckets in account"""

        logger.info('load_buckets')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_buckets
        resp = self.client.list_buckets()
        # pprint.pprint(resp)

        self.buckets = resp.get('Buckets',[])
        logger.info(f'LoadBuckets: Number of Bucket found: {len(self.buckets)}')

        # Get region for each bucket
        for bucket in self.buckets:
            try :
                resp = self.client.get_bucket_location( Bucket=bucket['Name'])
            except self.client.exceptions.NoSuchBucket :
                bucket['Region'] = 'Deleted'
                continue

            bucket['Region'] = resp.get('LocationConstraint','NA')
            if bucket['Region'] is None:
                bucket['Region'] = 'us-east-1'

        # pprint.pprint(self.buckets)

        return self


    #*************************************************
    #
    #*************************************************
    def load_folder(self):
        """Load all content of a bucket and prefix"""

        logger.info('load_folder')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2
        paginator = self.client.get_paginator('list_objects_v2')
        contents = []
        common_prefixes = []
        param={
            'Bucket': self.bucket,
            'Prefix': self.prefix,
            'Delimiter': '/'
        }

        for page in paginator.paginate(**param):
            contents.extend(page.get('Contents', []))
            common_prefixes.extend(page.get('CommonPrefixes', []))


        # To all commonPrefixes, add the attribute Key
        for common_prefixe in common_prefixes:
            common_prefixe['Key'] = common_prefixe['Prefix']

        self.objects = common_prefixes + contents

        # To all objects, set a name without the prefix
        for obj in self.objects:
            obj['_Name'] = obj['Key'].replace(self.prefix, '', 1)

        return self

    #*************************************************
    #
    #*************************************************
    def load_object(self):
        """Load all content of a bucket and prefix"""

        logger.info('load_folder')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
        self.s3_object = self.client.get_object_attributes(
            Bucket=self.bucket,
            Key=self.key,
            ObjectAttributes=['ETag','Checksum','ObjectParts','StorageClass','ObjectSize']
        )

        return self


    #*************************************************
    #
    #*************************************************
    def get_presigned_url(self):
        """Get a presigned URL for the object"""

        expiration = o7i.input_int('Expiration (seconds) :')

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html#S3.Client.generate_presigned_url
        url = self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': self.key
            },
            ExpiresIn=expiration
        )

        print(f'Presigned URL: {url}')



    # To Download file
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/download_file.html

    # Download directory, example from chat gpt:
    # import os
    # import boto3

    # # Initialize a session using Amazon S3
    # s3 = boto3.client('s3')

    # # Create an S3 resource object
    # s3_resource = boto3.resource('s3')

    # # S3 bucket and folder details
    # bucket_name = 'my-bucket'
    # folder_name = 'my-folder/'

    # # Local directory to save the files
    # local_directory = './local-folder'

    # # Make sure the local directory exists
    # if not os.path.exists(local_directory):
    #     os.makedirs(local_directory)

    # # Initialize paginator and iterate through each page (helps with large number of files)
    # paginator = s3.get_paginator('list_objects_v2')
    # for page in paginator.paginate(Bucket=bucket_name, Prefix=folder_name):
    #     # Download each file individually
    #     for obj in page['Contents']:
    #         key = obj['Key']
    #         path, filename = os.path.split(key)
    #         save_path = os.path.join(local_directory, filename)

    #         # Download the file
    #         print(f"Downloading {key} to {save_path}")
    #         s3_resource.meta.client.download_file(bucket_name, key, save_path)


    #*************************************************
    #
    #*************************************************
    def upload_file(self):
        """Upload a file to a bucket"""

        logger.info(f'UploadFile to {self.bucket}/{self.prefix}')

        file_path = o7fe.FileExplorer(cwd = '.').select_file()
        file_key = os.path.basename(file_path)


        if not o7i.is_it_ok(f'Upload {file_key} to {self.bucket}/{self.prefix} ?') :
            return self

        if self.prefix :
            file_key = f'{self.prefix}/{file_key}'

        response = self.client.upload_file(file_path, self.bucket, file_key)
        pprint.pprint(response)

        return self


    #*************************************************
    #
    #*************************************************
    def upload_file_obj(self, bucket : str, key : str, file_path : str):
        """Upload a file to a bucket, used by other module"""

        logger.info(f'UploadFile {bucket=} {key=} {file_path=}')

        ret = None

        with open(file_path, 'rb') as fileobj:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_fileobj
            resp = self.client.upload_fileobj(fileobj, Bucket=bucket, Key=key,)
            logger.info(f'UploadFile: Done {resp=}')
            ret = f'https://s3-external-1.amazonaws.com/{bucket}/{key}'

        return ret

    #*************************************************
    #
    #*************************************************
    def display_object(self):
        """Display the active object"""

        self.load_object()

        print()
        print(f'Bucket: {self.bucket}')
        print(f'Prefix: {self.prefix}')
        print(f'Name  : {self.key}')
        print()
        print(f'Last Modified: {self.s3_object.get("LastModified", "-")}')
        print(f'Storage Class: {self.s3_object.get("StorageClass", "-")}')
        print(f'ETag: {self.s3_object.get("ETag", "-")}')
        print(f'Size: {o7f.to_bytes(self.s3_object.get("ObjectSize", "-"))}')

        print()

    #*************************************************
    #
    #*************************************************
    def display_buckets(self):
        """Display the list buckets"""

        self.load_buckets()

        params = TableParam(
            columns = [
                ColumnParam(title = 'id',          type = 'i',    min_width = 4  ),
                ColumnParam(title = 'Name',     type = 'str',  data_col = 'Name'),
                ColumnParam(title = 'Created', type = 'datetime',  data_col = 'CreationDate'),
                ColumnParam(title = 'Region',        type = 'str', data_col = 'Region')
            ]
        )
        print()
        Table(params, self.buckets).print()

        return self


    #*************************************************
    #
    #*************************************************
    def display_folder(self):
        """Display the list buckets"""


        print('')
        print(f'Bucket: {self.bucket}')
        print(f'Prefix: {self.prefix}')

        self.load_folder()

        params = TableParam(
            columns = [
                ColumnParam(title = 'id',           type = 'i',    min_width = 4  ),
                ColumnParam(title = 'Name',         type = 'str',  data_col = '_Name'),
                ColumnParam(title = 'Size',         type = 'bytes',  data_col = 'Size'),
                ColumnParam(title = 'Last Modified',type = 'datetime', data_col = 'LastModified'),
                ColumnParam(title = 'Storage',      type = 'str', data_col = 'StorageClass')
            ]
        )
        print()
        Table(params, self.objects).print()


    #*************************************************
    #
    #*************************************************
    def menu_object(self, index : int):
        """S3 Folder menu"""

        if  not 0 < index <= len(self.objects):
            return self

        s3_object = self.objects[index-1]

        if 'ETag' not in s3_object:
            self.prefix = s3_object['Key']
            return self

        self.key = s3_object['Key']

        obj = o7m.Menu(
            exit_option = 'b',
            title=f'S3 Folder - {self.bucket}',
            title_extra=self.session_info(), compact=False
        )
        obj.add_option(o7m.Option(key='r', name='Raw',callback=lambda: pprint.pprint(self.s3_object)))
        obj.add_option(o7m.Option(key='p', name='Presigned ', callback=self.get_presigned_url))

        obj.display_callback = self.display_object
        obj.loop()

        return self




    #*************************************************
    #
    #*************************************************
    def menu_folder(self, index : int):
        """S3 Folder menu"""

        if  not 0 < index <= len(self.buckets):
            return self

        self.bucket = self.buckets[index-1]['Name']
        self.prefix = ""
        self.key = ""

        obj = o7m.Menu(
            exit_option = 'b',
            title=f'S3 Folder - {self.bucket}',
            title_extra=self.session_info(), compact=True
        )
        obj.add_option(o7m.Option(key='r', name='Raw',callback=lambda: pprint.pprint(self.objects)))
        obj.add_option(o7m.Option(key='u', name='Upload',callback=self.upload_file))
        obj.add_option(o7m.Option(key='int', name='Details', callback=self.menu_object))


        obj.display_callback = self.display_folder
        obj.loop()


    #*************************************************
    #
    #*************************************************
    def menu_buckets(self):
        """S3 main menu"""

        obj = o7m.Menu(exit_option = 'b', title='S3 Bucket', title_extra=self.session_info(), compact=True)

        obj.add_option(o7m.Option(
            key='r',
            name='Display Raw Data',
            short='Raw',
            callback=lambda: pprint.pprint(self.buckets)
        ))
        obj.add_option(o7m.Option(
            key='int',
            name='Details for a bucket',
            short='Details',
            callback=self.menu_folder
        ))


        obj.display_callback = self.display_buckets
        obj.loop()

        return self

#*************************************************
#
#*************************************************
def menu(**kwargs):
    """Run Main Menu"""
    S3(**kwargs).menu_buckets()


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )



    # the_s3 = S3().menu_buckets()

    the_s3 = S3()
    the_s3.bucket = "my-bucket"
    # the_s3.prefix = ""
    the_s3.key = "my-file.zip"
    # the_s3.display_folder()

    the_s3.display_object()

    # theS3.MenuBuckets()
