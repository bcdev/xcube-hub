from typing import Optional
from kubernetes import client
from xcube_gen import api


def create_user_namespace(user_name: Optional[str] = None):
    api_pod_instance = client.CoreV1Api()
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=user_name))

    try:
        namespace = api_pod_instance.create_namespace(body=body)
    except BaseException as e:
        return api.ApiResponse.error(e, 400)

    return api.ApiResponse.success(namespace)
