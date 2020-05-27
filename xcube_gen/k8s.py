from kubernetes import client

from xcube_gen.xg_types import JsonObject


def create_deployment_object(name: str, container_name: str, image: str, container_port: int, config: JsonObject):
    # Configureate Pod template container
    envs = [
        client.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=config.get('secretAccessKey')),
        client.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=config.get('accessKeyId')),
    ]

    container = client.V1Container(
        name=container_name,
        image=image,
        command=["bash", "-c",
                 f"source activate xcube && xcube serve --prefix {name} --aws-env -P 4000 -A 0.0.0.0 "
                 f"{config.get('bucketUrl')}"],
        env=envs,
        ports=[client.V1ContainerPort(container_port=container_port)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": container_name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template,
        selector={'matchLabels': {'app': container_name}})
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment, namespace: str = 'default'):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=namespace)
    print("Deployment created. status='%s'" % str(api_response.status))


def delete_deployment(api_instance, name: str, namespace: str = 'default'):
    # Delete deployment
    api_response = api_instance.delete_namespaced_deployment(
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


def delete_service(name: str, namespace: str = 'default'):
    api_instance = client.CoreV1Api()
    api_instance.delete_namespaced_service(name=name, namespace=namespace)


def list_service(name: str, namespace: str = 'default'):
    api_instance = client.CoreV1Api()
    return api_instance.list_namespaced_service(namespace=namespace)


def create_xcube_serve_ingress_object(name: str, service_name: str, service_port: int, user_id: str):
    body = client.NetworkingV1beta1Ingress(
        api_version="networking.k8s.io/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=name),
        spec=client.NetworkingV1beta1IngressSpec(
            rules=[client.NetworkingV1beta1IngressRule(
                host="xcube-gen.brockmann-consult.de",
                http=client.NetworkingV1beta1HTTPIngressRuleValue(
                    paths=[client.NetworkingV1beta1HTTPIngressPath(
                        path="/" + user_id,
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


def create_xcube_genserv_ingress(ingress, namespace: str = 'default'):
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)

    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    networking_v1_beta1_api.create_namespaced_ingress(
        namespace=namespace,
        body=ingress
    )


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
