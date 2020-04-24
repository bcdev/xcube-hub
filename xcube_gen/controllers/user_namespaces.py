from typing import Optional
from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api


def create(user_id: Optional[str] = None):
    api_pod_instance = client.CoreV1Api()
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=user_id))

    try:
        namespace = api_pod_instance.create_namespace(body=body)
        return api.ApiResponse.success(str(namespace))
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def exists(user_id: str):
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        user_namespace_names = [namespace.metadata.name for namespace in namespaces]
        return api.ApiResponse.success(user_id in user_namespace_names)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def list():
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        return api.ApiResponse.success([namespace.metadata.name for namespace in namespaces.items])
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete(user_id: str):
    api_pod_instance = client.CoreV1Api()

    try:
        api_pod_instance.delete_namespace(name=user_id)
        return api.ApiResponse.success(user_id)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))

