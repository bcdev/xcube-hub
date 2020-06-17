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
import os
import uuid
from pprint import pprint
from typing import Optional, Union

from kubernetes import client
from kubernetes.client.rest import ApiException
# from rq import Queue, Connection

from xcube_gen import api
from xcube_gen.cache import Cache
from xcube_gen.controllers import user_namespaces
from xcube_gen.xg_types import AnyDict, Error


def create_sh_job_object(job_id: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> client.V1Job:
    # Configureate Pod template container
    sh_client_id = os.environ.get("SH_CLIENT_ID")
    sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
    sh_instance_id = os.environ.get("SH_INSTANCE_ID")
    sh_image = os.environ.get("XCUBE_SH_DOCKER_IMG")

    if not sh_image:
        raise api.ApiError(400, "Could not find any xcube-sh docker image.")

    if not sh_client_secret or not sh_client_id or not sh_instance_id:
        raise api.ApiError(400, "SentinelHub credentials invalid. Please contact Brockmann Consult")

    if cfg is not None:
        cmd = ["/bin/bash", "-c", f"source activate xcube && echo \'{json.dumps(cfg)}\' "
                                  f"| xcube sh {sh_cmd}"]
    else:
        cmd = ["/bin/bash", "-c", f"source activate xcube &&  xcube sh {sh_cmd}"]

    sh_envs = [
        client.V1EnvVar(name="SH_CLIENT_ID", value=sh_client_id),
        client.V1EnvVar(name="SH_CLIENT_SECRET", value=sh_client_secret),
        client.V1EnvVar(name="SH_INSTANCE_ID", value=sh_instance_id),
    ]

    container = client.V1Container(
        name="xcube-gen",
        image=sh_image,
        command=cmd,
        env=sh_envs)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "xcube-gen"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=1)
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_id),
        spec=spec)

    return job


def create(user_id: str, sh_cmd: str, cfg: AnyDict) -> Union[AnyDict, Error]:
    try:
        user_namespaces.create_if_not_exists(user_id=user_id)
        job_id = f"xcube-gen-{str(uuid.uuid4())}"
        cfg['xcube-gen-cfg'] = {'user_id': user_id, 'job_id': job_id}

        job = create_sh_job_object(job_id, sh_cmd=sh_cmd, cfg=cfg)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=user_id)

        cache = Cache()
        cache.set(job_id, cfg)

        return api.ApiResponse.success({'job_id': job_id, 'status': api_response.status.to_dict()})
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete_one(user_id: str, job_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.delete_namespaced_job(
            name=job_id,
            namespace=user_id,
            body=client.V1DeleteOptions(propagation_policy='Background', grace_period_seconds=5))
        return api.ApiResponse.success(api_response.status)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete_all(user_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.delete_collection_namespaced_job(namespace=user_id)
        return api.ApiResponse.success(api_response.status)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


# noinspection PyShadowingBuiltins
def list(user_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.list_namespaced_job(namespace=user_id)
        jobs = api_response.items
        res = [{'job_id': job.metadata.name,
                'status': {
                    'active': job.status.active,
                    'start_time': job.status.start_time,
                    'failed': job.status.failed,
                    'succeeded': job.status.succeeded,
                    'completion_time': job.status.completion_time,
                }} for job in jobs]
        return api.ApiResponse.success(res)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def status(user_id: str, job_id: str) -> AnyDict:
    api_instance = client.BatchV1Api()
    api_response = api_instance.read_namespaced_job_status(namespace=user_id, name=job_id)

    return api_response.status.to_dict()


def logs(user_id: str, job_id: str) -> AnyDict:
    api_pod_instance = client.CoreV1Api()

    pods = api_pod_instance.list_namespaced_pod(namespace=user_id, label_selector=f"job-name={job_id}")
    lgs = []
    for pod in pods.items:
        name = pod.metadata.name
        lg = api_pod_instance.read_namespaced_pod_log(namespace=user_id, name=name)
        lgs = lg.splitlines()

    return lgs


def get(user_id: str, job_id: str) -> Union[AnyDict, Error]:
    try:
        output = logs(user_id=user_id, job_id=job_id)
        stat = status(user_id=user_id, job_id=job_id)
        return api.ApiResponse.success({'job_id': job_id, 'status': stat, 'output': output})
    except ApiException as e:
        pprint(str(e))
        raise api.ApiError(e.status, str(e))
