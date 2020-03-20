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

from xcube_gen.batch import Batch
import uuid

from xcube_gen.types import AnyDict
from xcube_gen.version import version


def process(request: AnyDict) -> AnyDict:
    batch = Batch()

    try:
        job_name = f"xcube-gen-{str(uuid.uuid4())}"
        result = batch.create_job(job_name=job_name, sh_cmd='gen', cfg=request)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def jobs(request: AnyDict) -> AnyDict:
    batch = Batch()
    print(request)
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


def info() -> AnyDict:
    batch = Batch()
    try:
        job_name = f"xcube-gen-{str(uuid.uuid4())}"
        result = batch.get_info(job_name=job_name)
    except Exception as e:
        result = {'xcube-gen-error': str(e)}

    return result


def main() -> AnyDict:
    return {'xcube-gen': {'version': version}}
