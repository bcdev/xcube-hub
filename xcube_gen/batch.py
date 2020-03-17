from pprint import pprint
from typing import Dict, Any, Sequence
import json

from kubernetes import client, config

AnyDict = Dict[str, Any]

# config.load_incluster_config()
config.load_kube_config()


class Batch:
    def __init__(self, namespace: str = "default", image: str = "quay.io/bcdev/xcube-sh:0.4.0.dev0"):
        self._namespace = namespace
        self._image = image
        self._cmd = ["/bin/bash", "-c", "source activate xcube && xcube sh gen"]

    def create_job_object(self, job_name: str, config: Dict[str, Any]) -> client.V1Job:
        # Configureate Pod template container
        cmd = ["/bin/bash", "-c", f"source activate xcube && echo \'{json.dumps(config)}\' | xcube sh gen"]
        container = client.V1Container(
            name="xcube-gen",
            image=self._image,
            command=cmd)
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "xcube-gen"}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=4)
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name=job_name),
            spec=spec)

        return job

    def create_job(self, job_name: str, config: AnyDict) -> AnyDict:
        job = self.create_job_object(job_name, config=config)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(
            body=job,
            namespace=self._namespace)

        print("Job created. status='%s'" % str(api_response.status))
        return {key: getattr(api_response.status, key) for key in api_response.status.attribute_map}

    def delete_job(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.delete_namespaced_job(
            name=job_name,
            async_req=True,
            namespace=self._namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
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
        res = [{'name': job.metadata.name} for job in jobs]
        return res

    def get_status(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.read_namespaced_job_status(
            namespace=self._namespace,
            name=job_name
        )

        return api_response.status.conditions[0].to_dict()

    def get_result(self, job_name: str):
        api_instance = client.BatchV1Api()
        api_response = api_instance.read_namespaced_job(
            namespace=self._namespace,
            name=job_name,
            pretty=True
        )

        return api_response.to_dict()

