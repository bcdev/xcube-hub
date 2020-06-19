from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api
from xcube_gen.typedefs import AnyDict


def get_pods(user_id: str, job_id: str) -> AnyDict:
    api_pod_instance = client.CoreV1Api()
    try:
        pods = api_pod_instance.list_namespaced_pod(namespace=user_id, label_selector=f"job-name={job_id}")
        return api.ApiResponse.success(pods.items)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))

