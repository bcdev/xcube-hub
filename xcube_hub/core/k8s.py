import base64
from typing import Optional, Sequence, Union, Dict
from kubernetes import client
from kubernetes.client import V1Pod, V1PodList, NetworkingV1beta1Ingress, ApiException, ApiTypeError, ApiValueError, \
    CoreV1Api
from xcube_hub.typedefs import JsonObject

from xcube_hub import api


def get_secret(name: str, secret_item: str, namespace: str, v1_client: Optional[CoreV1Api] = None) -> str:
    v1_client = v1_client or client.CoreV1Api()

    try:
        secret = v1_client.read_namespaced_secret(name=name, namespace=namespace)
    except Exception as e:
        raise api.ApiError(400, str(e))

    if secret_item not in secret.data:
        raise api.ApiError(400, f"System Error: Secret {secret_item} not found in secret {name}.")

    return base64.b64decode(secret.data[secret_item]).decode()


def create_pvc_object(user_id: str, storage: str = '2Gi'):
    pvc = client.V1PersistentVolumeClaim(
        metadata={'name': 'claim-' + user_id},
        spec=client.V1PersistentVolumeClaimSpec(
            storage_class_name="standard",
            access_modes=['ReadWriteOnce', ],
            resources=client.V1ResourceRequirements(
                requests={'storage': storage}
            )
        )
    )

    return pvc


def create_pvc(pvc: client.V1PersistentVolumeClaim, namespace: str, core_api: Optional[client.CoreV1Api] = None):
    core_v1_api = core_api or client.CoreV1Api()
    try:
        core_v1_api.create_namespaced_persistent_volume_claim(namespace=namespace, body=pvc)
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when creating the pvc {pvc.metadata.name}: {str(e)}")


def create_pvc_if_not_exists(pvc: client.V1PersistentVolumeClaim, namespace: str):
    core_v1_api = client.CoreV1Api()

    try:
        pvcs = core_v1_api.list_namespaced_persistent_volume_claim(namespace=namespace)
    except (ApiException, ApiTypeError, ApiValueError) as e:
        raise api.ApiError(400, f"Error when creating the pvc {pvc.metadata.name}: {str(e)}")

    pvcs = [pvc.metadata.name for pvc in pvcs.items]
    if len(pvcs) == 0:
        create_pvc(pvc, namespace=namespace)
        return True

    return False


def create_goofys_daemonset_object(name: str, user_id: str, envs: Sequence):
    envs = [] if not envs else envs

    container = client.V1Container(
        name=name,
        image="quay.io/bcdev/cate-s3-daemon:0.1",
        command=["/usr/local/bin/goofys", "-o", "allow_other", "--uid", "1000", "--gid", "1000", "-f", "--region",
                 "eu-central-1", "eurodatacube:" + user_id, "/var/s3"],
        env=envs,
        image_pull_policy="Always",
        volume_mounts=[
            {
                "mountPath": '/dev/fuse',
                "name": "devfuse-" + user_id,
            },
            {
                "mountPath": "var/s3:shared",
                "name": 'mnt-goofys-' + user_id,
            },
        ],
        security_context=client.V1SecurityContext(privileged=True, capabilities={'add': ["SYS_ADMIN"]})
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name, "purpose": "cate-webapi"}),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=[
                {
                    'name': 'devfuse-' + user_id,
                    'hostPath': {'path': '/dev/fuse'}
                },
                {
                    'name': 'mnt-goofys-' + user_id,
                    'hostPath': {'path': '/var/s3'}
                }],
            security_context=client.V1PodSecurityContext(fs_group=1000)
        )
    )

    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={'matchLabels': {'app': name}}
    )

    daemon_set = client.V1DaemonSet(
        metadata=client.V1ObjectMeta(name=name, labels={"app": name, "purpose": "cate-webapi"}),
        spec=spec,
    )

    return daemon_set


def create_goofys_daemonset(daemonset: client.V1DaemonSet,
                            namespace: str = 'default',
                            core_api: Optional[client.AppsV1Api] = None):
    # Create deployment
    apps_v1_api = core_api or client.AppsV1Api()
    try:
        api_response = apps_v1_api.create_namespaced_daemon_set(
            body=daemonset,
            namespace=namespace)
        print("Deployment created. status='%s'" % str(api_response.status))
    except (ApiException, ApiTypeError, ApiValueError) as e:
        raise api.ApiError(400, f"Error when creating the deployment {daemonset.metadata.name}: {str(e)}")


def list_goofys_daemonsets(namespace: str, core_api: Optional[client.AppsV1Api] = None):
    api_instance = core_api or client.AppsV1Api()
    try:
        return api_instance.list_namespaced_daemon_set(namespace)
    except (ApiException, ApiTypeError, ApiValueError) as e:
        raise api.ApiError(400, f"Error when listing daemonsets in namespace {namespace}: {str(e)}")


def get_goofys_daemonset(namespace: str, name: str):
    daemonsets = list_goofys_daemonsets(namespace=namespace)
    for daemonset in daemonsets.items:
        if daemonset.metadata.name == name:
            return daemonset

    return None


def delete_goofys_daemonset(name: str, namespace: str = 'default', core_api: Optional[client.AppsV1Api] = None):
    apps_v1_api = core_api or client.AppsV1Api()

    try:
        api_response = apps_v1_api.delete_namespaced_daemon_set(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print("Daemonset deleted. status='%s'" % str(api_response.status))
    except (ApiException, ApiTypeError, ApiValueError) as e:
        raise api.ApiError(400, f"Error when deleting the deployment {name}: {str(e)}")


def create_goofys_daemonset_if_not_exists(namespace: str, daemonset: client.V1DaemonSet):
    daemonset_exists = get_goofys_daemonset(namespace=namespace, name=daemonset.metadata.name)

    if daemonset_exists is None:
        create_goofys_daemonset(daemonset=daemonset, namespace=namespace)


def create_deployment_object(name: str, user_id: str,
                             container_name: str,
                             image: str,
                             container_port: int,
                             command: Optional[Union[str, Sequence[str]]] = None,
                             envs: Optional[Sequence] = None,
                             volume_mounts: Optional[Sequence] = None,
                             volumes: Optional[Sequence] = None,
                             init_containers: Optional[Sequence] = None,
                             limits: Optional[Dict] = None,
                             requests: Optional[Dict] = None,
                             annotations: Optional[Dict] = None,
                             labels: Optional [Dict] = None):
    # Configureate Pod template container
    envs = [] if not envs else envs

    container = client.V1Container(
        name=container_name,
        image=image,
        resources=client.V1ResourceRequirements(limits=limits, requests=requests),
        command=command,
        env=envs,
        image_pull_policy="Always",
        ports=[client.V1ContainerPort(container_port=container_port)],
        volume_mounts=volume_mounts,
        security_context=client.V1SecurityContext(privileged=True)
    )

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={"app": container_name, "purpose": "webapi"},
            annotations=annotations
        ),
        spec=client.V1PodSpec(
            containers=[container],
            volumes=volumes,
            init_containers=init_containers,
            security_context=client.V1PodSecurityContext(fs_group=1000)
        )
    )
    # Create the specification of deployment
    labels = labels or {}
    labels['app'] = container_name
    match_labels = {'matchLabels': labels}
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector=match_labels
    )
    # Instantiate the deployment object

    metadata = client.V1ObjectMeta(name=name, labels=labels)
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=metadata,
        spec=spec)

    return deployment


def create_deployment(deployment: client.V1Deployment,
                      namespace: str = 'default',
                      core_api: Optional[client.AppsV1Api] = None):
    # Create deployment
    apps_v1_api = core_api or client.AppsV1Api()
    try:
        api_response = apps_v1_api.create_namespaced_deployment(
            body=deployment,
            namespace=namespace)
        return api_response.status
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when creating the deployment {deployment.metadata.name}: {str(e)}")


def create_deployment_if_not_exists(namespace: str, deployment: client.V1Deployment):
    deployment_exists = get_deployment(namespace=namespace, name=deployment.metadata.name)

    if deployment_exists is None:
        return create_deployment(deployment=deployment, namespace=namespace)

    return False


def delete_deployment(name: str, namespace: str = 'default', core_api: Optional[client.AppsV1Api] = None):
    apps_v1_api = core_api or client.AppsV1Api()

    try:
        api_response = apps_v1_api.delete_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print("Deployment deleted. status='%s'" % str(api_response.status))
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when deleting the deployment {name}: {str(e)}")


def list_deployments(namespace: str, core_api: Optional[client.AppsV1Api] = None):
    api_instance = core_api or client.AppsV1Api()
    try:
        return api_instance.list_namespaced_deployment(namespace)
    except (ApiException, ApiTypeError, ApiValueError) as e:
        raise api.ApiError(400, f"Error when listing deployment in namespace {namespace}: {str(e)}")


def get_deployment(namespace: str, name: str):
    deployments = list_deployments(namespace=namespace)

    for deployment in deployments.items:
        if deployment.metadata.name == name:
            return deployment

    return None


def create_service_object(name: str, port: int, target_port: int):
    service = client.V1Service()
    service.api_version = "v1"
    service.kind = "Service"
    service.metadata = client.V1ObjectMeta(name=name)
    spec = client.V1ServiceSpec()
    spec.selector = {"app": name}
    spec.ports = [client.V1ServicePort(protocol="TCP", port=port, target_port=target_port)]
    service.spec = spec

    return service


def create_service(service, namespace: str = 'default', core_api: Optional[client.CoreV1Api] = None):
    api_instance = core_api or client.CoreV1Api()
    try:
        api_instance.create_namespaced_service(namespace=namespace, body=service)
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when creating the service {service.metadata.name}: {str(e)}")


def create_service_if_not_exists(service, namespace: str = 'default'):
    if not has_service(service.metadata.name, namespace=namespace):
        create_service(service=service, namespace=namespace)


def delete_service(name: str, namespace: str = 'default', core_api: Optional[client.CoreV1Api] = None):
    api_instance = core_api or client.CoreV1Api()
    try:
        api_instance.delete_namespaced_service(name=name, namespace=namespace)
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when deleting the service {name}: {str(e)}")


def list_services(namespace: str = 'default', core_api: Optional[client.CoreV1Api] = None):
    api_instance = core_api or client.CoreV1Api()
    try:
        return api_instance.list_namespaced_service(namespace=namespace)
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when listing services in namespace {namespace}: {str(e)}")


def has_service(name: str, namespace: str = 'default'):
    services = list_services(namespace=namespace)
    services = [service.metadata.name for service in services.items]
    return name in services


def create_ingress_object(name: str,
                          service_name: str,
                          service_port: int,
                          user_id: str,
                          host_uri: str,
                          annotations: Optional[Sequence] = None,
                          path_regex: str = "/.*"
                          ) -> client.NetworkingV1beta1Ingress:
    webapi_host = host_uri.replace("https://", "").replace("http://", "")
    annotations = annotations or {
        "proxy_set_header": "Upgrade $http_upgrade; Connection \"upgrade\"",
        "nginx.ingress.kubernetes.io/proxy-connect-timeout": "86400",
        "nginx.ingress.kubernetes.io/proxy-read-timeout": "86400",
        "nginx.ingress.kubernetes.io/proxy-send-timeout": "86400",
        "nginx.ingress.kubernetes.io/send-timeout": "86400",
        "nginx.ingress.kubernetes.io/proxy-body-size": "2000m",
        "nginx.ingress.kubernetes.io/enable-cors": "true",
        "nginx.ingress.kubernetes.io/websocket-services": service_name
    }

    body = client.NetworkingV1beta1Ingress(
        api_version="networking.k8s.io/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=name, annotations=annotations),
        spec=client.NetworkingV1beta1IngressSpec(
            rules=[client.NetworkingV1beta1IngressRule(
                host=webapi_host,
                http=client.NetworkingV1beta1HTTPIngressRuleValue(
                    paths=[client.NetworkingV1beta1HTTPIngressPath(
                        path="/" + user_id + path_regex,
                        backend=client.NetworkingV1beta1IngressBackend(
                            service_port=service_port,
                            service_name=service_name)

                    )]
                )
            )
            ]
        )
    )
    return body


def create_ingress(ingress: client.NetworkingV1beta1Ingress, namespace: str = 'default',
                   core_api: Optional[client.NetworkingV1beta1Api] = None):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = core_api or client.NetworkingV1beta1Api()

    try:
        networking_v1_beta1_api.create_namespaced_ingress(
            namespace=namespace,
            body=ingress
        )
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when creating the ingress {ingress.metadata.name}: {str(e)}")


def patch_ingress(name: str, body, namespace: str = 'default', core_api: Optional[client.NetworkingV1beta1Api] = None):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = core_api or client.NetworkingV1beta1Api()
    try:
        networking_v1_beta1_api.patch_namespaced_ingress(
            name=name,
            namespace=namespace,
            body=body
        )
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when patching the ingress {name}: {str(e)}")


def create_ingress_if_not_exists(ingress, namespace: str = 'default'):
    ingresses = list_ingresses(namespace=namespace)
    ingresses = [ingress.metadata.name for ingress in ingresses.items]
    if len(ingresses) == 0:
        create_ingress(ingress, namespace)


def delete_ingress(name, namespace: str = 'default', core_api: Optional[client.NetworkingV1beta1Api] = None):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = core_api or client.NetworkingV1beta1Api()
    try:
        networking_v1_beta1_api.delete_namespaced_ingress(
            namespace=namespace,
            name=name
        )
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when deleting the ingress {name}: {str(e)}")


def list_ingresses(namespace: str = 'default', core_api: Optional[client.NetworkingV1beta1Api] = None):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = core_api or client.NetworkingV1beta1Api()
    try:
        return networking_v1_beta1_api.list_namespaced_ingress(namespace=namespace)
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when listing ingresses in namespace {namespace}: {str(e)}")


def get_ingress(namespace: str, name: str) -> Optional[NetworkingV1beta1Ingress]:
    ingresses = list_ingresses(namespace=namespace)
    for ingress in ingresses.items:
        if ingress.metadata.name == name:
            return ingress

    return None


def get_pod(prefix: str, namespace: Optional[str] = None, label_selector: str = None) -> Optional[V1Pod]:
    pods = list_pods(namespace=namespace, label_selector=label_selector)

    res = None
    for pod in pods.items:
        if pod.metadata.name.startswith(prefix):
            res = pod

    return res


def list_pods(namespace: Optional[str] = None, label_selector: str = None,
              core_api: Optional[client.CoreV1Api] = None) -> V1PodList:
    v1 = core_api or client.CoreV1Api()

    try:
        if namespace:
            if label_selector:
                pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            else:
                pods = v1.list_namespaced_pod(namespace=namespace)
        else:
            if label_selector:
                pods = v1.list_pod_for_all_namespaces(label_selector=label_selector)
            else:
                pods = v1.list_pod_for_all_namespaces()
    except (ApiException, ApiTypeError) as e:
        raise api.ApiError(400, f"Error when listing pods in namespace {namespace or 'All'}: {str(e)}")

    return pods


def count_pods(namespace: Optional[str] = None, label_selector: str = None) -> int:
    pods = list_pods(namespace=namespace, label_selector=label_selector)
    if pods:
        return len(pods.items)
    else:
        return 0


def create_configmap_object(name: str, data: JsonObject) -> client.V1ConfigMap:
    return client.V1ConfigMap(metadata=client.V1ObjectMeta(name=name), data=data)


def create_configmap(namespace: str, body: client.V1ConfigMap, core_api: Optional[client.CoreV1Api] = None):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    try:
        core_api = core_api or client.CoreV1Api()
        core_api.create_namespaced_config_map(namespace=namespace, body=body)
    except (ApiException, ApiValueError) as e:
        raise api.ApiError(400,
                           f"Error when creating the configmap {body.metadata.name} in {namespace or 'All'}: {str(e)}")
