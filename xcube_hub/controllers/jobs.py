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
from typing import Union, Sequence

from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_hub import api
from xcube_hub.auth0 import Auth0
from xcube_hub.controllers import user_namespaces
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.typedefs import AnyDict, Error


def create_gen_job_object(job_id: str, cfg: AnyDict) -> client.V1Job:
    # Configure Pod template container
    sh_client_id = os.environ.get("SH_CLIENT_ID")
    sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
    sh_instance_id = os.environ.get("SH_INSTANCE_ID")
    gen_image = os.environ.get("XCUBE_DOCKER_IMG")
    gen_container_pull_policy = os.environ.get("XCUBE_GEN_DOCKER_PULL_POLICY")

    if not gen_image:
        raise api.ApiError(400, "Could not find any xcube-sh docker image.")

    if not sh_client_secret or not sh_client_id or not sh_instance_id:
        raise api.ApiError(400, "SentinelHub credentials invalid. Please contact Brockmann Consult")

    if not cfg:
        raise api.ApiError(400, "create_gen_job_object needs a config dict.")

    cmd = ["/bin/bash", "-c", f"source activate xcube && echo \'{json.dumps(cfg)}\' "
                              f"| xcube --traceback gen2 -v --store-conf /etc/xcube/data-pools.yaml"]

    sh_envs = [
        client.V1EnvVar(name="SH_CLIENT_ID", value=sh_client_id),
        client.V1EnvVar(name="SH_CLIENT_SECRET", value=sh_client_secret),
        client.V1EnvVar(name="SH_INSTANCE_ID", value=sh_instance_id),
    ]

    volume_mounts = [
        {
            'name': 'xcube-datapools',
            'mountPath': '/etc/xcube',
            'readOnly': True
        }, ]

    volumes = [
        {
            'name': 'xcube-datapools',
            'configMap': {
                'name': 'xcube-datapools'
            }
        }, ]

    container = client.V1Container(
        name="xcube-gen",
        image=gen_image,
        command=cmd,
        volume_mounts=volume_mounts,
        image_pull_policy=gen_container_pull_policy,
        env=sh_envs)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "xcube-gen"}),
        spec=client.V1PodSpec(
            volumes=volumes,
            restart_policy="Never",
            containers=[container]
        ))
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


def create(user_id: str, cfg: AnyDict) -> Union[AnyDict, Error]:
    try:
        xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
        user_namespaces.create_if_not_exists(user_namespace=xcube_hub_namespace)
        callback_uri = os.getenv('XCUBE_HUB_CALLBACK_URL', False)
        if callback_uri is False:
            raise api.ApiError(400, "XCUBE_HUB_CALLBACK_URL must be given")

        job_id = f"xcube-gen-{str(uuid.uuid4())}"

        cfg['callback_config'] = dict(api_uri=callback_uri + f'/jobs/{user_id}/{job_id}/callback',
                                      access_token=Auth0.get_token_auth_header())

        cfg['output_config']['data_id'] = job_id + '.zarr'

        job = create_gen_job_object(job_id, cfg=cfg)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=xcube_hub_namespace)

        kvdb = KeyValueDatabase.instance()
        kvdb.set(job_id, cfg)

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
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.delete_collection_namespaced_job(namespace=xcube_hub_namespace)
        return api.ApiResponse.success(api_response.status)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


# noinspection PyShadowingBuiltins
def list(user_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.list_namespaced_job(namespace=xcube_hub_namespace)
        jobs = api_response.items

        res = []
        for job in jobs:
            lgs = logs(user_id=user_id, job_id=job.metadata.name)
            res.append({'job_id': job.metadata.name,
                        'status': {
                            'active': job.status.active,
                            'start_time': job.status.start_time,
                            'failed': job.status.failed,
                            'succeeded': job.status.succeeded,
                            'completion_time': job.status.completion_time,
                            'output': lgs,
                        }})

        return api.ApiResponse.success(res)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def status(user_id: str, job_id: str) -> AnyDict:
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    api_instance = client.BatchV1Api()
    try:
        api_response = api_instance.read_namespaced_job_status(namespace=xcube_hub_namespace, name=job_id)
    except (client.ApiValueError, client.ApiException) as e:
        print(str(e))
        return {}

    return api_response.status.to_dict()


def logs(user_id: str, job_id: str) -> Sequence:
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    api_pod_instance = client.CoreV1Api()

    lgs = []
    try:
        pods = api_pod_instance.list_namespaced_pod(namespace=xcube_hub_namespace, label_selector=f"job-name={job_id}")

        for pod in pods.items:
            name = pod.metadata.name

            lg = api_pod_instance.read_namespaced_pod_log(namespace=xcube_hub_namespace, name=name)

            lgs.append(lg)
    except (client.ApiValueError, client.ApiException) as e:
        pprint(str(e))

    return lgs


def get(user_id: str, job_id: str) -> Union[AnyDict, Error]:
    try:
        output = logs(user_id=user_id, job_id=job_id)
        stat = status(user_id=user_id, job_id=job_id)

        if 'failed' in stat and stat['failed']:
            raise api.ApiError(400, message=f"Job {job_id} failed", output='\n'.join(output))

        return api.ApiResponse.success({'job_id': job_id, 'status': stat, 'output': output})
    except ApiException as e:
        pprint(str(e))
        raise api.ApiError(e.status, str(e))
