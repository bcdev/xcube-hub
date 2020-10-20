from typing import Optional
from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_hub import api


def create_if_not_exists(user_id: Optional[str] = None):
    api_pod_instance = client.CoreV1Api()
    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=user_id))

    try:
        if not exists(user_id):
            api_pod_instance.create_namespace(body=body)
            return True
        else:
            return False
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def exists(user_id: str):
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        user_namespace_names = [namespace.metadata.name for namespace in namespaces.items]
        return user_id in user_namespace_names
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def list():
    api_pod_instance = client.CoreV1Api()

    try:
        namespaces = api_pod_instance.list_namespace()
        return [namespace.metadata.name for namespace in namespaces.items]
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def delete(user_id: str):
    api_pod_instance = client.CoreV1Api()

    try:
        api_pod_instance.delete_namespace(name=user_id)
        return True
    except ApiException as e:
        raise api.ApiError(e.status, str(e))

