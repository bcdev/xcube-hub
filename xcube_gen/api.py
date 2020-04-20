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

import uuid
from typing import Any, Tuple, Union

from xcube_gen.batch import Batch
from xcube_gen.types import AnyDict
from xcube_gen.version import version


def job(request: AnyDict) -> AnyDict:
    batch = Batch()

    try:
        job_name = f"xcube-gen-{str(uuid.uuid4())}"
        result = batch.create_job(job_name=job_name, sh_cmd='gen', cfg=request)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def jobs() -> AnyDict:
    batch = Batch()

    try:
        result = {'jobs': batch.list_jobs()}
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def job_delete(request: AnyDict) -> AnyDict:
    batch = Batch()
    job_name = request['job_name']
    try:
        result = {'delete': batch.delete_job(job_name)}
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def job_status(job_name: str) -> AnyDict:
    batch = Batch()
    try:
        return batch.get_status(job_name)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def job_result(job_name: str) -> AnyDict:
    batch = Batch()
    try:
        result = batch.get_result(job_name)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def jobs_delete(request: AnyDict) -> AnyDict:
    batch = Batch()
    job_names = request['job_names']
    try:
        result = {'delete': batch.delete_jobs(job_names)}
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def jobs_purge(request: AnyDict) -> AnyDict:
    batch = Batch()
    try:
        result = {'purge': batch.purge_jobs()}
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def job_info() -> AnyDict:
    batch = Batch()
    try:
        job_name = f"xcube-gen-{str(uuid.uuid4())}"
        result = batch.get_info(job_name=job_name)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def main() -> AnyDict:
    return {'xcube-gen': {'version': version}}


def get_request_entry(request: AnyDict,
                      key: str,
                      value_type: Union[type, Tuple[type, ...]] = str,
                      item_type: Union[type, Tuple[type, ...]] = None,
                      item_count: int = None,
                      default_value=UNDEFINED,
                      path: str = None) -> Any:
    path = path + '/' + key if path else key
    if key in request:
        value = request[key]
    else:
        if default_value is UNDEFINED:
            raise ApiError(400, f'missing request entry "{path}"')
        value = default_value
    if not isinstance(value, value_type):
        raise ApiError(400, f'request entry "{path}" is of wrong type, expected {value_type}')
    if isinstance(value, list):
        if item_count is not None and len(value) != item_count:
            raise ApiError(400, f'request entry "{path}" must be a list of length {item_count}')
        if item_type is not None:
            for v in value:
                if not isinstance(v, item_type):
                    raise ApiError(400, f'request entry "{path}" has an item of wrong type, expected {item_type}')
    return value


class ApiError(BaseException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    @property
    def response(self):
        return dict(message=self.message), self.status_code
