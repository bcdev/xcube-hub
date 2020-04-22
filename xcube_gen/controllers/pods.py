from typing import Union

from kubernetes import client

from xcube_gen import api
from xcube_gen.types import AnyDict, Error


def get_pods(user_name: str, job_id: str) -> Union[AnyDict, Error]:
    api_pod_instance = client.CoreV1Api()
    try:
        pods = api_pod_instance.list_namespaced_pod(namespace=user_name, label_selector=f"job-name={job_id}")
    except BaseException as e:
        return api.ApiResponse.error(e, 400)

    return api.ApiResponse.success(pods.items)
