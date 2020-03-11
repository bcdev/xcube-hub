from pprint import pprint

from kubernetes import client, config

config.load_kube_config()


class Batch:
    def __init__(self, namespace: str = "default", image: str = "quay.io/bcdev/xcube-python-deps:0.3.0"):
        self._namespace = namespace
        self._image = image
        self._cmd = ["/bin/bash", "-c", "source activate xcube && xcube"]

    def create_job_object(self, job_name: str):
        # Configureate Pod template container
        container = client.V1Container(
            name="xcube-gen",
            image=self._image,
            command=self._cmd)
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

    def create_job(self, job_name: str):
        job = self.create_job_object(job_name)
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
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))

        print("Job deleted. status='%s'" % str(api_response.status))
        return api_response.status

    def list_jobs(self):
        api_instance = client.BatchV1Api()
        api_response = api_instance.list_namespaced_job(namespace=self._namespace)
        pprint(api_response)
        jobs = api_response.items
        res = [{'name': job.metadata.name} for job in jobs]
        return res
