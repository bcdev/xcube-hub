import json
import os
import uuid
from pprint import pprint
from typing import Union, Sequence, Optional

from kubernetes import client
from kubernetes.client import ApiException
from urllib3.exceptions import MaxRetryError

from xcube_hub import api
from xcube_hub.auth0 import get_token_auth_header
from xcube_hub.core import callbacks
from xcube_hub.core import user_namespaces
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.typedefs import AnyDict, Error


def get(user_id: str, cubegen_id: str) -> Union[AnyDict, Error]:
    try:
        output = logs(user_id=user_id, job_id=cubegen_id)
        stat = status(user_id=user_id, job_id=cubegen_id)
        progress = callbacks.get_callback(user_id=user_id, cubegen_id=cubegen_id)

        if 'failed' in stat and stat['failed']:
            raise api.ApiError(400, message=f"Cubegen {cubegen_id} failed", output='\n'.join(output))
        if not stat:
            raise api.ApiError(404, message=f"Cubegen {cubegen_id} not found")

        return {'cubegen_id': cubegen_id, 'status': stat, 'output': output, 'progress': progress}
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def create_cubegen_object(cubegen_id: str, cfg: AnyDict) -> client.V1Job:
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
        raise api.ApiError(400, "create_gen_cubegen_object needs a config dict.")

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
    # Instantiate the cubegen object
    cubegen = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=cubegen_id),
        spec=spec)

    return cubegen


def create(user_id: str, cfg: AnyDict, token: Optional[str] = None) -> Union[AnyDict, Error]:
    try:
        if 'input_config' not in cfg and 'input_configs' not in cfg:
            raise api.ApiError(400, "Either 'input_config' or 'input_configs' must be given")

        xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
        user_namespaces.create_if_not_exists(user_namespace=xcube_hub_namespace)
        callback_uri = os.getenv('XCUBE_HUB_CALLBACK_URL', False)

        if callback_uri is False:
            raise api.ApiError(400, "XCUBE_HUB_CALLBACK_URL must be given")

        job_id = f"{user_id}-{str(uuid.uuid4())[:18]}"

        cfg['callback_config'] = dict(api_uri=callback_uri + f'/cubegens/{job_id}/callbacks',
                                      access_token=token or get_token_auth_header())

        cfg['output_config']['data_id'] = job_id + '.zarr'

        job = create_cubegen_object(job_id, cfg=cfg)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=xcube_hub_namespace)

        kvdb = KeyValueDatabase.instance()
        kvdb.set(user_id + '__' + job_id + '__cfg', cfg)

        return {'cubegen_id': job_id, 'status': api_response.status.to_dict()}
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, message=str(e))


# noinspection PyShadowingBuiltins
def list(user_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.list_namespaced_job(namespace=xcube_hub_namespace)

        res = []
        for job in api_response.items:
            if user_id in job.metadata.name:
                lgs = logs(user_id=user_id, job_id=job.metadata.name)
                res.append({'cubegen_id': job.metadata.name,
                            'status': {
                                'active': job.status.active,
                                'start_time': job.status.start_time,
                                'failed': job.status.failed,
                                'succeeded': job.status.succeeded,
                                'completion_time': job.status.completion_time,
                                'output': lgs,
                            }})

        return api.ApiResponse.success(res)
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


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
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        pprint(str(e))

    return lgs


def status(user_id: str, job_id: str) -> AnyDict:
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    api_instance = client.BatchV1Api()
    try:
        api_response = api_instance.read_namespaced_job_status(namespace=xcube_hub_namespace, name=job_id)
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        print(str(e))
        return {}

    return api_response.status.to_dict()


def delete_one(cubegen_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.delete_namespaced_job(
            name=cubegen_id,
            namespace=xcube_hub_namespace,
            body=client.V1DeleteOptions(propagation_policy='Background', grace_period_seconds=5))
        return api_response.status
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def delete_all(user_id: str) -> Union[AnyDict, Error]:
    try:
        jobs = list(user_id=user_id)
        for job in jobs['result']:
            delete_one(job['cubegen_id'])
        return api.ApiResponse.success("SUCCESS")
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))
