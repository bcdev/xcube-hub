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
import os.path
import uuid
from typing import Any, Tuple, Union, Optional

from xcube_gen.controllers.jobs import create_job, JobError, list_jobs, delete_job, get_job_status
from xcube_gen.types import AnyDict, UNDEFINED, JsonObject, JsonValue
from xcube_gen.version import version


class ApiResponse:

    @classmethod
    def success(cls, result: Any = None) -> AnyDict:
        response = dict(status='ok')
        if result is not None:
            response['result'] = result
        return response

    @classmethod
    def error(cls, error: Union[str, BaseException] = None, status_code: int = 500) -> Tuple[AnyDict, int]:
        response = dict(status='error')
        if error is not None:
            response['message'] = f'{error}'
        return response, status_code


class ApiError(BaseException):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code

    @property
    def response(self):
        return ApiResponse.error(error=self, status_code=self.status_code)


def job(request: AnyDict) -> AnyDict:
    try:
        job_name = f"xcube-gen-{str(uuid.uuid4())}"
        namespace = request['namespace']

        return create_job(namespace=namespace, job_name=job_name, sh_cmd='gen', cfg=request)
    except JobError as e:
        raise ApiError(400, str(e))


def jobs(request: AnyDict) -> AnyDict:
    try:
        namespace = request['namespace']
        result = {'jobs': list_jobs(namespace=namespace)}
    except JobError as e:
        raise ApiError(400, str(e))

    return result


def job_delete(request: AnyDict) -> AnyDict:
    job_name = request['job_name']
    namespace = request['namespace']
    try:
        return delete_job(namespace=namespace, job_name=job_name)
    except JobError as e:
        raise ApiError(str(e))


def job_status(job_name: str) -> AnyDict:
    try:
        namespace = request['namespace']
        return get_job_status(job_name)
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


def jobs_purge() -> AnyDict:
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


def datastores() -> AnyDict:
    datastores_path = os.path.join(os.path.dirname(__file__), 'resources', 'datastores.json')
    with open(datastores_path) as fp:
        return json.load(fp)


def main() -> AnyDict:
    return {'xcube-gen': {'version': version}}


def get_json_request_value(request: JsonObject,
                           key: str,
                           value_type: Union[type, Tuple[type, ...]] = str,
                           item_type: Union[type, Tuple[type, ...]] = None,
                           item_count: int = None,
                           default_value: JsonValue = UNDEFINED,
                           key_path: str = None) -> JsonValue:
    if not isinstance(request, dict):
        raise ApiError(400, f'request must be a JSON object')
    if key in request:
        value = request[key]
    else:
        if default_value is UNDEFINED:
            raise ApiError(400, f'missing request key "{_join_key_path(key_path, key)}"')
        value = default_value
    if not isinstance(value, value_type):
        raise ApiError(400,
                       f'value for request key "{_join_key_path(key_path, key)}" is of wrong type: '
                       f'expected type {value_type}, got type {type(value)}')
    if isinstance(value, (list, tuple)):
        if item_count is not None and len(value) != item_count:
            raise ApiError(400,
                           f'value for request key "{_join_key_path(key_path, key)}" must be a '
                           f'list of length {item_count}, got length {len(value)}')
        if item_type is not None:
            for v in value:
                if not isinstance(v, item_type):
                    raise ApiError(400,
                                   f'value for request key "{_join_key_path(key_path, key)}" has an item of wrong type: '
                                   f'expected type {item_type}, got type {type(v)}')
    return value


def _join_key_path(key_path: Optional[str], key: str) -> str:
    return (key_path + '/' + key) if key_path else key
