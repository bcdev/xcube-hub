import json
import os
from typing import Optional, Union

from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api
from xcube_gen.types import AnyDict, Error


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


def create(user_name: str, job_id: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> Union[AnyDict, Error]:
    try:
        job = create_sh_job_object(job_id, sh_cmd=sh_cmd, cfg=cfg)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=user_name)
        return api.ApiResponse.success({'job': job_id, 'status': api_response.status.to_dict()})
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete_one(user_name: str, job_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.delete_namespaced_job(
            name=job_id,
            namespace=user_name,
            body=client.V1DeleteOptions(propagation_policy='Background', grace_period_seconds=5))
        return api.ApiResponse.success(api_response.status)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete_all(user_name: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.delete_collection_namespaced_job(namespace=user_name)
        return api.ApiResponse.success(api_response.status)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


# noinspection PyShadowingBuiltins
def list(user_name: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()

    try:
        api_response = api_instance.list_namespaced_job(namespace=user_name)
        jobs = api_response.items
        res = [{'name': job.metadata.name,
                'start_time': job.status.start_time,
                'failed': job.status.failed,
                'succeeded': job.status.succeeded,
                'completion_time': job.status.completion_time,
                } for job in jobs]
        return api.ApiResponse.success(res)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def status(user_name: str, job_id: str) -> AnyDict:
    api_instance = client.BatchV1Api()
    api_response = api_instance.read_namespaced_job_status(namespace=user_name, name=job_id)

    return api_response.status.to_dict()


def result(user_name: str, job_id: str) -> AnyDict:
    api_pod_instance = client.CoreV1Api()

    pods = api_pod_instance.list_namespaced_pod(namespace=user_name, label_selector=f"job-name={job_id}")
    logs = []
    for pod in pods.items:
        name = pod.metadata.name
        log = api_pod_instance.read_namespaced_pod_log(namespace=user_name, name=name)
        logs = log.splitlines()

    return logs


def get(user_name: str, job_id: str) -> Union[AnyDict, Error]:
    try:
        output = result(user_name=user_name, job_id=job_id)
        stat = status(user_name=user_name, job_id=job_id)
        return {'job_id': job_id, 'status': stat, 'output': output}
    except ApiException as e:
        raise api.ApiError(e.status, str(e))