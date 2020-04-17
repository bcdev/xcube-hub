import json
import os
import threading
from datetime import datetime
from pprint import pprint
from typing import Sequence, Optional

from kubernetes import client

from xcube_gen.types import AnyDict


class BatchError(ValueError):
    pass


class Batch:
    _config_lock = threading.Lock()
    _config_loaded = False

    def __init__(self, namespace: Optional[str] = None, image: Optional[str] = None):
        self._load_config_once()

        self._namespace = namespace or os.environ.get('K8S_NAMESPACE') or 'default'

        self._image = image or os.environ.get("XCUBE_SH_DOCKER_IMG")

        if not self._image:
            raise BatchError("xcube-sh docker image is not configured.")

        self._cmd = ["/bin/bash", "-c", "source activate xcube && xcube sh gen"]

    def create_sh_job_object(self, job_name: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> client.V1Job:
        # Configureate Pod template container
        sh_client_id = os.environ.get("SH_CLIENT_ID")
        sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
        sh_instance_id = os.environ.get("SH_INSTANCE_ID")

        if not sh_client_secret or not sh_client_id or not sh_instance_id:
            raise BatchError("SentinelHub credentials invalid. Please contact Brockmann Consult")

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
            image=self._image,
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

    def create_job(self, job_name: str, sh_cmd: str, cfg: Optional[AnyDict] = None) -> AnyDict:
        job = self.create_sh_job_object(job_name, sh_cmd=sh_cmd, cfg=cfg)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(
            body=job,
            namespace=self._namespace)

        print("Job created. status='%s'" % str(api_response.status))
        return {'job_name': job_name, 'status': api_response.status.to_dict()}

    def delete_job(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_namespaced_job(
            name=job_name,

            namespace=self._namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Background',
                grace_period_seconds=5))

        print("Job deleted. status='%s'" % str(api_response.status))
        return api_response.status

    def delete_jobs(self, job_names: Sequence[str]) -> Sequence[AnyDict]:
        stati = []
        for job_name in job_names:
            status = self.delete_job(job_name)
            stati.append({job_name: status})

        return stati

    def purge_jobs(self):
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_collection_namespaced_job(namespace=self._namespace)

        print(f"All Jobs in {self._namespace} deleted.")

        return api_response.status

    def list_jobs(self) -> Sequence[AnyDict]:
        api_instance = client.BatchV1Api()
        api_response = api_instance.list_namespaced_job(namespace=self._namespace)
        pprint(api_response)
        jobs = api_response.items
        res = [{'name': job.metadata.name,
                'start_time': job.status.start_time,
                'failed': job.status.failed,
                'succeeded': job.status.succeeded,
                'completion_time': job.status.completion_time,
                } for job in jobs]
        return res

    def get_status(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.read_namespaced_job_status(
            namespace=self._namespace,
            name=job_name
        )

        return api_response.status.to_dict()

    def get_result(self, job_name: str) -> AnyDict:
        api_pod_instance = client.CoreV1Api()

        logs = []
        for pod in self.get_pods(job_name=job_name):
            name = pod.metadata.name
            log = api_pod_instance.read_namespaced_pod_log(namespace=self._namespace, name=name)
            logs = log.splitlines()

        return {'job_name': job_name, 'logs': logs}

    def get_pods(self, job_name: str):
        api_pod_instance = client.CoreV1Api()

        pods = api_pod_instance.list_namespaced_pod(namespace=self._namespace, label_selector=f"job-name={job_name}")

        return pods.items

    def get_info(self, job_name: str):
        self.create_job(job_name=job_name, sh_cmd='info')
        timeout = 120
        start_time = datetime.now()
        while True:
            now = datetime.now()
            if (now - start_time).seconds > timeout:
                raise BatchError(f"Timeout after {timeout}s.")
            status = self.get_status(job_name=job_name)
            if status['succeeded']:
                break

        return self.get_result(job_name=job_name)

    @classmethod
    def _load_config_once(cls):
        if not cls._config_loaded:
            cls._config_lock.acquire()
            if not cls._config_loaded:
                cls._load_config()
                cls._config_loaded = True
            cls._config_lock.release()

    @classmethod
    def _load_config(cls):
        from kubernetes import config
        if os.environ.get('RUN_LOCAL'):
            print("Kubernetes configured to run locally.")
            config.load_kube_config()
        else:
            config.load_incluster_config()
