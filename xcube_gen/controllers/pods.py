from kubernetes import client


def get_pods(user: str, job_name: str):
    api_pod_instance = client.CoreV1Api()

    pods = api_pod_instance.list_namespaced_pod(namespace=user, label_selector=f"job-name={job_name}")

    return pods.items
