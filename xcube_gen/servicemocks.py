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

import concurrent.futures
import datetime
import time
import uuid
from typing import List

import flask

import xcube_gen.api as api
from xcube_gen.types import JsonObject

JOB_ID_KEY = 'job_id'


def extend_app(app, prefix: str):
    @app.route(prefix + '/mock/jobs/<user_id>', methods=['GET', 'PUT', 'DELETE'])
    def _mock_jobs(user_id: str):
        if flask.request.method == 'GET':
            jobs = get_jobs(user_id)
            return api.ApiResponse.success(jobs)
        if flask.request.method == 'PUT':
            job = new_job(user_id, flask.request.json)
            print(job)
            return api.ApiResponse.success(job)
        if flask.request.method == 'DELETE':
            delete_jobs(user_id)
            return api.ApiResponse.success()

    @app.route(prefix + '/mock/jobs/<user_id>/<job_id>', methods=['GET', 'DELETE'])
    def _mock_job(user_id: str, job_id: str):
        if flask.request.method == "GET":
            job = get_job(user_id, job_id)
            return api.ApiResponse.success(job)
        if flask.request.method == "DELETE":
            delete_job(user_id, job_id)
            return api.ApiResponse.success()

    @app.route(prefix + '/mock/cubes/<user_id>/viewer', methods=['POST'])
    def _mock_cubes_viewer(user_id: str):
        if flask.request.method == "POST":
            result = launch_viewer(user_id, flask.request.json)
            return api.ApiResponse.success(result)


_USER_JOBS = dict()

_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=3)


def new_job(user_id: str, request: JsonObject) -> JsonObject:
    job_id = f"xcube-gen-{str(uuid.uuid4())}"
    job = {
        JOB_ID_KEY: job_id,
        "status": {
            "start_time": None,
            "completion_time": None,
            "active": None,
            "conditions": None,
            "succeeded": None,
            "failed": None,
        }
    }
    jobs = _USER_JOBS.get(user_id, {})
    jobs[job_id] = job
    _USER_JOBS[user_id] = jobs
    _EXECUTOR.submit(_run_job, user_id, job_id, request.get('duration', 10))
    return job


def get_job(user_id: str, job_id: str) -> JsonObject:
    return _USER_JOBS.get(user_id, {}).get(job_id)


def get_jobs(user_id: str) -> List[JsonObject]:
    return [v for v in _USER_JOBS.get(user_id, {}).values()]


def delete_job(user_id: str, job_id: str, delete_duration: float = 3):
    _EXECUTOR.submit(_delete_job, user_id, job_id, delete_duration)


def delete_jobs(user_id: str, delete_duration: float = 3):
    jobs = get_jobs(user_id)
    num_jobs = len(jobs)
    for job in jobs:
        delete_job(user_id, job[JOB_ID_KEY],
                   delete_duration=delete_duration / num_jobs)


def launch_viewer(user_id: str, output_config: JsonObject, launch_duration: float = 4) -> JsonObject:
    print(f'Launching viewer for {user_id} and {output_config}')
    time.sleep(launch_duration)
    return dict(viewerUri='http://viewer.demo.dcs4cop.eu',
                serverUri='http://localhost:8080')


def _run_job(user_id: str, job_id: str, job_duration: float):
    job = get_job(user_id, job_id)
    if not job:
        return

    status = job['status']
    status['active'] = True
    status['start_time'] = str(datetime.datetime.now())

    num_steps = 100
    for i in range(num_steps):
        job = get_job(user_id, job_id)
        if not job:
            return

        # status = job['status']
        # conditions = status.get("conditions") or []
        # conditions.append({
        #     "last_probe_time": str(datetime.datetime.now()),
        #     "last_transition_time": str(datetime.datetime.now()),
        #     "message": f"Job in progress: {i}% done",
        #     "reason": "All good",
        #     "status": "True",
        #     "type": "Success"
        # })
        # status["conditions"] = conditions

        time.sleep(job_duration / num_steps)

    job = get_job(user_id, job_id)
    if not job:
        return

    status = job['status']
    status['active'] = False
    status['succeeded'] = True
    status['failed'] = 0
    status['completion_time'] = str(datetime.datetime.now())


def _delete_job(user_id: str, job_id: str, delete_duration: float):
    time.sleep(delete_duration)
    if user_id in _USER_JOBS:
        jobs = _USER_JOBS[user_id]
        if job_id in jobs:
            del jobs[job_id]
