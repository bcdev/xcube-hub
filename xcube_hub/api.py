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

import datetime
from typing import Any, Tuple, Union, Optional, Dict

from xcube_hub.typedefs import AnyDict, UNDEFINED, JsonObject, JsonValue

SERVER_NAME = 'xcube-gen-api'
SERVER_DESCRIPTION = 'xcube Generator Service'
SERVER_START_TIME = datetime.datetime.now().isoformat()


class ApiResponse:

    @classmethod
    def success(cls, result: Optional[Any] = None, status_code: int = 200, message: Optional[str] = None) -> \
            Tuple[AnyDict, int]:
        return result, status_code

    @classmethod
    def error(cls,
              error: Optional[Union[str, BaseException]] = None,
              output: Optional[Union[str, BaseException]] = None,
              traceback: Optional[Union[str, BaseException]] = None,
              status_code: int = 500,
              result: Optional[Dict] = None) -> Tuple[AnyDict, int]:
        response = dict()

        result = result or {}
        if error is not None:
            response['message'] = f'{error}'
            result['message'] = f'{error}'
        if output is not None:
            response['output'] = f'{output}'

        if traceback is not None:
            response['traceback'] = f'{traceback}'

        result['status'] = 'error'
        response['job_id'] = 'unknown'
        response['job_status'] = {'active': 0, 'failed': 1, 'succeeded': 0}
        response['job_result'] = result

        return response, status_code


class ApiError(BaseException):
    def __init__(self, status_code: int,
                 message: str,
                 output: Optional[str] = None,
                 result: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self._output = output
        self._result = result

    @property
    def response(self):
        import traceback
        return ApiResponse.error(error=self,
                                 status_code=self.status_code,
                                 output=self._output,
                                 traceback=traceback.format_exc(),
                                 result=self._result)


def get_json_request_value(request: JsonObject,
                           key: str,
                           value_type: Union[type, Tuple[type, ...]] = None,
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
    if value_type is not None and not isinstance(value, value_type):
        raise ApiError(400,
                       f'value for request key "{_join_key_path(key_path, key)}" is of wrong type: '
                       f'expected type {_type_name(value_type)}, got type {_type_name(type(value))}')
    if isinstance(value, (list, tuple)):
        if item_count is not None and len(value) != item_count:
            raise ApiError(400,
                           f'value for request key "{_join_key_path(key_path, key)}" must be a '
                           f'{_type_name(type(value))} of length {item_count}, got length {len(value)}')
        if item_type is not None:
            for v in value:
                if not isinstance(v, item_type):
                    raise ApiError(400,
                                   f'value for request key "{_join_key_path(key_path, key)}" has an item of wrong type: '
                                   f'expected type {_type_name(item_type)}, got type {_type_name(type(v))}')
    return value


def _join_key_path(key_path: Optional[str], key: str) -> str:
    return (key_path + '/' + key) if key_path else key


def _type_name(value_type: Union[type, Tuple[type, ...]]):
    if isinstance(value_type, type):
        return value_type.__name__
    else:
        return ' or '.join(_type_name(t) for t in value_type)
