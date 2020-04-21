import json
import os
from typing import Optional, Sequence

from kubernetes import client
from xcube_gen.controllers.pods import get_pods
from xcube_gen.types import AnyDict


class JobError(ValueError):
    pass


def create_sh_job_object(job_name: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> client.V1Job:
    # Configureate Pod template container
    sh_client_id = os.environ.get("SH_CLIENT_ID")
    sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
    sh_instance_id = os.environ.get("SH_INSTANCE_ID")
    sh_image = os.environ.get("XCUBE_SH_DOCKER_IMG")

    if not sh_image:
        raise JobError("Could not find any xcube-sh docker image.")

    if not sh_client_secret or not sh_client_id or not sh_instance_id:
        raise JobError("SentinelHub credentials invalid. Please contact Brockmann Consult")

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
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec)

    return job


def create_job(user: str, job_name: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> AnyDict:
    job = create_sh_job_object(job_name, sh_cmd=sh_cmd, cfg=cfg)
    api_instance = client.BatchV1Api()
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace=user)

    print("Job created. status='%s'" % str(api_response.status))
    return {'job': job_name, 'status': api_response.status.to_dict()}


def delete_job(user: str, job_name: str):
    api_instance = client.BatchV1Api()
    api_response = api_instance.delete_namespaced_job(
        name=job_name,

        namespace=user,
        body=client.V1DeleteOptions(
            propagation_policy='Background',
            grace_period_seconds=5))

    print("Job deleted. status='%s'" % str(api_response.status))
    return api_response.status


def delete_jobs(user: str, job_names: Sequence[str]) -> Sequence[AnyDict]:
    stati = []
    for job_name in job_names:
        status = delete_job(user, job_name)
        stati.append({job_name: status})

    return stati


def purge_jobs(user: str):
    api_instance = client.BatchV1Api()
    api_response = api_instance.delete_collection_namespaced_job(namespace=user)

    print(f"All Jobs in {user} deleted.")

    return api_response.status


def list_jobs(user: str) -> Sequence[AnyDict]:
    api_instance = client.BatchV1Api()
    api_response = api_instance.list_namespaced_job(namespace=user)

    jobs = api_response.items
    res = [{'name': job.metadata.name,
            'start_time': job.status.start_time,
            'failed': job.status.failed,
            'succeeded': job.status.succeeded,
            'completion_time': job.status.completion_time,
            } for job in jobs]
    return res


def get_job_status(user: str, job_name: str):
    api_instance = client.BatchV1Api()
    api_response = api_instance.read_namespaced_job_status(
        namespace=user,
        name=job_name
    )

    return api_response.status.to_dict()


def get_result(user: str, job_name: str) -> AnyDict:
    api_pod_instance = client.CoreV1Api()

    logs = []
    for pod in get_pods(user=user, job_name=job_name):
        name = pod.metadata.name
        log = api_pod_instance.read_namespaced_pod_log(namespace=user, name=name)
        logs = log.splitlines()

    return {'job_name': job_name, 'logs': logs}
