from typing import Optional
from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api


def create(user_name: Optional[str] = None):
    api_pod_instance = client.CoreV1Api()
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=user_name))

    try:
        namespace = api_pod_instance.create_namespace(body=body)
        return api.ApiResponse.success(str(namespace))
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def exists(user_name: str):
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        user_namespace_names = [namespace.metadata.name for namespace in namespaces]
        return api.ApiResponse.success(user_name in user_namespace_names)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def list():
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        return api.ApiResponse.success([namespace.metadata.name for namespace in namespaces.items])
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete(user_name: str):
    api_pod_instance = client.CoreV1Api()

    try:
        api_pod_instance.delete_namespace(name=user_name)
        return api.ApiResponse.success(user_name)
    except ApiException as e:
        raise api.ApiError(e.status, str(e))

