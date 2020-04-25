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

import flask

import xcube_gen.api as api

JOB_ID_KEY = 'job_id'


def extend_app(app, prefix: str):
    @app.route(prefix + '/mock/jobs/<user_id>', methods=['GET', 'POST', 'DELETE'])
    def _mock_jobs(user_id: str):
        if flask.request.method == 'GET':
            jobs = get_jobs(user_id)
            return api.ApiResponse.success(jobs)
        if flask.request.method == 'POST':
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


_USER_JOBS = dict()

_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=1)


def new_job(user_id: str, request: dict):
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


def get_job(user_id: str, job_id: str):
    return _USER_JOBS.get(user_id, {}).get(job_id)


def get_jobs(user_id: str):
    return [v for v in _USER_JOBS.get(user_id, {}).values()]


def delete_job(user_id: str, job_id: str):
    if user_id in _USER_JOBS:
        jobs = _USER_JOBS[user_id]
        if job_id in jobs:
            jobs[job_id]['active'] = False
            del jobs[job_id]


def delete_jobs(user_id: str):
    jobs = get_jobs(user_id)
    for job in jobs:
        delete_job(user_id, job[JOB_ID_KEY])


def _run_job(user_id: str, job_id: str, job_duration: float):
    job = get_job(user_id, job_id)
    if not job:
        return
    job['active'] = True
    job['start_time'] = str(datetime.datetime.now())

    num_steps = 100
    for i in range(num_steps):
        job = get_job(user_id, job_id)
        if not job:
            return

        # conditions = job.get("conditions") or []
        # conditions.appemd({
        #     "last_probe_time": str(datetime.datetime.now()),
        #     "last_transition_time": str(datetime.datetime.now()),
        #     "message": f"Job in progress: {i}% done",
        #     "reason": "All good",
        #     "status": "True",
        #     "type": "Success"
        # })
        # job["conditions"] = conditions

        time.sleep(job_duration / num_steps)

    job = get_job(user_id, job_id)
    if not job:
        return

    job['active'] = False
    job['succeeded'] = True
    job['failed'] = 0
    job['completion_time'] = str(datetime.datetime.now())
