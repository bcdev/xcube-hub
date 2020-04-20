# The MIT License (MIT)
# Copyright (c) 2020 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import threading
from typing import Optional

import boto3

from xcube_gen.types import AnyDict

DEFAULT_DB_PROFILE_NAME = 'default'
DEFAULT_DB_BUCKET_NAME = 'eurodatacube'
DEFAULT_DB_USER_DATA_KEY = 'users/{user_name}/data.json'


class Database:
    __doc__ = \
        f"""
        An object database that uses S3 as backend.
        
        Credentials are read from ``~/.aws/credentials, section [<profile_name>]``.
        Use ``aws configure [--profile <profile_name>]`` CLI command to configure a profile.
        See https://docs.aws.amazon.com/cli/latest/reference/configure/.
        
        :param profile_name: The AWS credentials profile. 
            Defaults to "{DEFAULT_DB_PROFILE_NAME}".
        :param bucket: The S3 bucket that stores database objects. 
            Defaults to "{DEFAULT_DB_BUCKET_NAME}".
        :param user_data_key: A key used to store user data. Must contain the string "{{user_name}}".
            Defaults to "{DEFAULT_DB_USER_DATA_KEY}".
        """

    _instance_lock = threading.Lock()
    _instance = None

    def __init__(self,
                 profile_name: str = DEFAULT_DB_PROFILE_NAME,
                 bucket_name: str = DEFAULT_DB_BUCKET_NAME,
                 user_data_key: str = DEFAULT_DB_USER_DATA_KEY):

        self._profile_name = profile_name
        self._bucket_name = bucket_name
        self._user_data_key = user_data_key

        self._session = boto3.Session(profile_name=profile_name)
        self._client = self._session.client('s3')

    @classmethod
    def instance(cls, **kwargs) -> "Database":
        """
        Return a database singleton.

        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """
        if cls._instance is None:
            cls._instance_lock.acquire()
            if cls._instance is None:
                cls._instance = Database(**kwargs)
            cls._instance_lock.release()
        return cls._instance

    @property
    def profile_name(self) -> str:
        return self._profile_name

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @property
    def user_data_key(self) -> str:
        return self._user_data_key

    def get_user_data(self, user_name: str) -> Optional[AnyDict]:
        try:
            response = self._client.get_object(**self._user_data_kwargs(user_name))
        except self._client.exceptions.NoSuchKey:
            return None
        # print('get_user_data:', response)
        object_data = self._check_response(response)
        if object_data is not None:
            return json.load(object_data, encoding='utf-8')
        else:
            raise DatabaseError('No data found')

    def put_user_data(self, user_name: str, user_data: AnyDict):
        object_data = json.dumps(user_data).encode('utf-8')
        response = self._client.put_object(**self._user_data_kwargs(user_name), Body=object_data)
        # print('put_user_data:', response)
        self._check_response(response)

    def delete_user_data(self, user_name: str):
        try:
            response = self._client.delete_object(**self._user_data_kwargs(user_name))
        except self._client.exceptions.NoSuchKey:
            return
        # print('delete_user_data:', response)
        self._check_response(response)

    def _user_data_kwargs(self, user_name: str):
        return dict(Bucket=self._bucket_name, Key=self._user_data_key.format(user_name=user_name))

    @classmethod
    def _check_response(cls, response: AnyDict):
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)
        if not (200 <= status_code < 300):
            raise DatabaseError(f'AWS S3 responded with HTTP status code {status_code}')
        return response.get('Body')


class DatabaseError(BaseException):
    """
    Raised by methods of :class:`Database`.
    """
    pass
