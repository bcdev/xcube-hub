from typing import Optional, Sequence, Union
from kubernetes import client
from kubernetes.client import V1Pod

from xcube_gen.poller import poll_deployment_status


def create_pvc_object(user_id: str, storage: str = '10Gi'):
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


def create_pvc(pvc: client.V1PersistentVolumeClaim, namespace: str):
    core_v1_api = client.CoreV1Api()
    core_v1_api.create_namespaced_persistent_volume_claim(namespace=namespace, body=pvc)


def create_pvc_if_not_exists(pvc: client.V1PersistentVolumeClaim, namespace: str):
    core_v1_api = client.CoreV1Api()

    pvcs = core_v1_api.list_namespaced_persistent_volume_claim(namespace=namespace)
    pvcs = [pvc.metadata.name for pvc in pvcs.items]
    if len(pvcs) == 0:
        create_pvc(pvc, namespace=namespace)


def create_deployment_object(name: str, user_id: str, container_name: str, image: str, container_port: int,
                             command: Union[str, Sequence[str]], envs: Optional[Sequence] = None):
    # Configureate Pod template container
    envs = [] if not envs else envs

    container = client.V1Container(
        name=container_name,
        image=image,
        command=command,
        env=envs,
        security_context=client.V1SecurityContext(run_as_user=1000, run_as_group=1000),
        image_pull_policy="Always",
        ports=[client.V1ContainerPort(container_port=container_port)],
        volume_mounts=[{'mountPath': "/home/cate", 'name': 'claim-' + user_id}]
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": container_name, "purpose": "cate-webapi"}),
        spec=client.V1PodSpec(
            security_context=client.V1PodSecurityContext(run_as_user=1000, run_as_group=1000, fs_group=1000),
            containers=[container],
            volumes=[{'name': 'claim-' + user_id, 'persistentVolumeClaim': {'claimName': 'claim-' + user_id}}, ]
        )
    )
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={'matchLabels': {'app': container_name}}
    )
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    return deployment


def create_deployment(deployment, namespace: str = 'default'):
    # Create deployement
    apps_v1_api = client.AppsV1Api()
    api_response = apps_v1_api.create_namespaced_deployment(
        body=deployment,
        namespace=namespace)
    print("Deployment created. status='%s'" % str(api_response.status))


def create_deployment_if_not_exists(namespace: str, deployment: client.V1Deployment):
    create = False
    apps_v1_api = client.AppsV1Api()
    deployments = apps_v1_api.list_namespaced_deployment(namespace=namespace)

    if len(deployments.items) == 0:
        create = True
    else:
        for dep in deployments.items:
            image_new = deployment.spec.template.spec.containers[0].image
            image_existing = dep.spec.template.spec.containers[0].image
            if dep.metadata.name == deployment.metadata.name and image_new != image_existing:
                delete_deployment(name=dep.metadata.name, namespace=namespace)
                poll_deployment_status(apps_v1_api.list_namespaced_deployment, status='empty', namespace=namespace)
                create = True

    if create:
        create_deployment(deployment=deployment, namespace=namespace)


def delete_deployment(name: str, namespace: str = 'default'):
    apps_v1_api = client.AppsV1Api()
    api_response = apps_v1_api.delete_namespaced_deployment(
        name=name,
        namespace=namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Deployment deleted. status='%s'" % str(api_response.status))


def list_deployments(api_instance, namespace: str):
    return api_instance.list_namespaced_deployment(namespace)


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


def create_service(service, namespace: str = 'default'):
    api_instance = client.CoreV1Api()
    api_instance.create_namespaced_service(namespace=namespace, body=service)


def create_service_if_not_exists(service, namespace: str = 'default'):
    services = list_service(name=service.metadata.name, namespace=namespace)
    services = [service.metadata.name for service in services.items]
    if len(services) == 0:
        create_service(service=service, namespace=namespace)


def delete_service(name: str, namespace: str = 'default'):
    api_instance = client.CoreV1Api()
    api_instance.delete_namespaced_service(name=name, namespace=namespace)


def list_service(name: str, namespace: str = 'default'):
    api_instance = client.CoreV1Api()
    return api_instance.list_namespaced_service(namespace=namespace)


def create_ingress_object(name: str, service_name: str, service_port: int, user_id: str, host_uri: str):
    webapi_host = host_uri
    if host_uri.startswith('https://'):
        webapi_host = host_uri.replace("https://", "")
    elif host_uri.startswith('http://'):
        webapi_host = host_uri.replace("http://", "")

    body = client.NetworkingV1beta1Ingress(
        api_version="networking.k8s.io/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=name, annotations={
            # "cert-manager.io/cluster-issuer": "letsencrypt",
            "nginx.ingress.kubernetes.io/rewrite-target": "/$1",
            "proxy_set_header": "Upgrade $http_upgrade; Connection \"upgrade\"",
            "nginx.ingress.kubernetes.io/proxy-connect-timeout": "1800",
            "nginx.ingress.kubernetes.io/proxy-read-timeout": "1800",
            "nginx.ingress.kubernetes.io/proxy-send-timeout": "1800",
            "nginx.ingress.kubernetes.io/send-timeout": "1800",
            "nginx.ingress.kubernetes.io/proxy-body-size": "2000m"
        }),
        spec=client.NetworkingV1beta1IngressSpec(
            # tls=client.NetworkingV1beta1IngressTLS(
            #     hosts=[webapi_host, ],
            #     secret_name='cate-tls'
            # ),
            rules=[client.NetworkingV1beta1IngressRule(
                host=webapi_host,
                http=client.NetworkingV1beta1HTTPIngressRuleValue(
                    paths=[client.NetworkingV1beta1HTTPIngressPath(
                        path="/" + user_id + "/(.*)",
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


def create_ingress(ingress, namespace: str = 'default'):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    networking_v1_beta1_api.create_namespaced_ingress(
        namespace=namespace,
        body=ingress
    )


def create_ingress_if_not_exists(ingress, namespace: str = 'default'):
    ingresses = list_ingress(namespace=namespace)
    ingresses = [ingress.metadata.name for ingress in ingresses.items]
    if len(ingresses) == 0:
        create_ingress(ingress, namespace)


def delete_ingress(name, namespace: str = 'default'):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    networking_v1_beta1_api.delete_namespaced_ingress(
        namespace=namespace,
        name=name
    )


def list_ingress(namespace: str = 'default'):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    return networking_v1_beta1_api.list_namespaced_ingress(namespace=namespace)


def get_pod(prefix: str, namespace: Optional[str] = None, label_selector: str = None) -> Union[type(None), V1Pod]:
    pods = get_pods(namespace=namespace, label_selector=label_selector)

    for pod in pods.items:
        if pod.metadata.name.startswith(prefix):
            return pod
    return None


def get_pods(namespace: Optional[str] = None, label_selector: str = None):
    v1 = client.CoreV1Api()

    if namespace:
        if label_selector:
            return v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
        else:
            return v1.list_namespaced_pod(namespace=namespace)
    else:
        if label_selector:
            return v1.list_pod_for_all_namespaces(label_selector=label_selector)
        else:
            return v1.list_pod_for_all_namespaces()


def count_pods(namespace: Optional[str] = None, label_selector: str = None) -> int:
    pods = get_pods(namespace=namespace, label_selector=label_selector)
    if pods:
        return len(pods.items)
    else:
        return 0
