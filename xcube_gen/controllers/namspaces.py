from typing import Optional
from kubernetes import client


def create_user_namespace(user: Optional[str] = None):
    api_pod_instance = client.CoreV1Api()

    body = client.V1Namespace(metadata=client.V1ObjectMeta(name=user))
    namespace = api_pod_instance.create_namespace(body=body)

    return namespace
