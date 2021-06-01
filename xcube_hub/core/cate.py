# The MIT License (MIT)
# Copyright (c) 2020 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import time
from typing import Optional

from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_hub import api, util
from xcube_hub.core import user_namespaces
from xcube_hub.core.k8s import create_deployment_object, create_service_object, \
    delete_deployment, delete_service, list_services, get_pod, \
    create_deployment_if_not_exists, create_service_if_not_exists, count_pods, \
    get_deployment, get_ingress, create_ingress_object, create_ingress
from xcube_hub.poller import poll_pod_phase
from xcube_hub.typedefs import JsonObject
from xcube_hub.util import raise_for_invalid_username


def delete_cate(user_id: str, prune: bool = False) -> bool:
    cate_namespace = os.environ.get("CATE_WEBAPI_NAMESPACE", "cate")

    user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

    deployment = get_deployment(name=user_id + '-cate', namespace=cate_namespace)

    if deployment:
        delete_deployment(name=user_id + '-cate', namespace=cate_namespace)

    if prune:
        service_name = user_id + '-cate'
        services = list_services(namespace=cate_namespace)
        services = [service.metadata.name for service in services.items]
        if service_name in services:
            delete_service(name=service_name, namespace=cate_namespace)

    return True


def launch_cate(user_id: str) -> JsonObject:
    try:
        max_pods = util.maybe_raise_for_env("CATE_MAX_WEBAPIS", default=50, typ=int)

        grace = util.maybe_raise_for_env("CATE_LAUNCH_GRACE", default=2, typ=int)

        raise_for_invalid_username(user_id)

        if count_pods(label_selector="purpose=cate-webapi") > max_pods:
            raise api.ApiError(413, "Too many pods running.")

        cate_image = util.maybe_raise_for_env("CATE_IMG")
        cate_version = util.maybe_raise_for_env("CATE_VERSION")
        cate_command = util.maybe_raise_for_env("CATE_COMMAND", False)
        cate_env_activate_command = util.maybe_raise_for_env("CATE_ENV_ACTIVATE_COMMAND", False)
        cate_webapi_uri = util.maybe_raise_for_env("CATE_WEBAPI_URI")
        cate_namespace = util.maybe_raise_for_env("WORKSPACE_NAMESPACE", "cate")
        cate_stores_config_path = util.maybe_raise_for_env("CATE_STORES_CONFIG_PATH")

        user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

        if not cate_command:
            cate_command = "cate-webapi-start -b -p 4000 -a 0.0.0.0 -r /home/cate/workspace"

        if not cate_env_activate_command:
            cate_env_activate_command = "source activate cate-env"

        if not cate_image:
            raise api.ApiError(400, "Could not find the cate webapi docker image.")

        cate_image = cate_image + ':' + cate_version

        command = ["/bin/bash", "-c", f"{cate_env_activate_command} && {cate_command}"]

        envs = [client.V1EnvVar(name='CATE_USER_ROOT', value="/home/cate/workspace"),
                client.V1EnvVar(name='CATE_STORES_CONFIG_PATH', value="/etc/cate/stores.yaml"),
                client.V1EnvVar(name='JUPYTERHUB_SERVICE_PREFIX', value='/' + user_id + '/')]

        volume_mounts = [
            {
                'name': 'workspace-pvc',
                'mountPath': '/home/cate/workspace',
                'subPath': user_id + '-scratch'
            },
            {
                'name': 'workspace-pvc',
                'mountPath': '/home/cate/.cate',
                'subPath': user_id + '-cate'
            },
            {
                'name': 'cate-stores',
                'mountPath': '/etc/cate',
                'readOnly': True
            },
        ]

        volumes = [
            {
                'name': 'workspace-pvc',
                'persistentVolumeClaim': {
                    'claimName': 'workspace-pvc',
                }
            },
            {
                'name': 'cate-stores',
                'configMap': {
                    'name': 'cate-stores'
                }
            },
        ]

        init_containers = [
            {
                "name": "fix-owner",
                "image": "bash",
                "command": ["chown", "-R", "1000.1000", "/home/cate/.cate", "/home/cate/workspace"],
                "volumeMounts": [
                    {
                        "mountPath": "/home/cate/.cate",
                        "subPath": user_id + '-cate',
                        "name": "workspace-pvc",
                    },
                    {
                        "mountPath": "/home/cate/workspace",
                        "subPath": user_id + '-scratch',
                        "name": "workspace-pvc",
                    },
                ]
            },
        ]

        deployment = create_deployment_object(name=user_id + '-cate',
                                              user_id=user_id,
                                              container_name=user_id + '-cate',
                                              image=cate_image,
                                              envs=envs,
                                              container_port=4000,
                                              command=command,
                                              volumes=volumes,
                                              volume_mounts=volume_mounts,
                                              init_containers=init_containers)

        # Make create_if_exists test for broken pods
        # pod_status = get_status(user_id)
        # if pod_status != "Running":
        #     create_deployment(namespace=user_id, deployment=deployment)
        # else:
        create_deployment_if_not_exists(namespace=cate_namespace, deployment=deployment)

        service = create_service_object(name=user_id + '-cate', port=4000, target_port=4000)
        create_service_if_not_exists(service=service, namespace=cate_namespace)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        service_name = user_id + '-cate'

        ingress = get_ingress(namespace=cate_namespace, name=service_name)
        if not ingress:
            ingress = create_ingress_object(name=service_name,
                                            service_name=service_name,
                                            service_port=4000,
                                            user_id=user_id,
                                            host_uri=host_uri)
            create_ingress(ingress, namespace=cate_namespace)

        # add_cate_path_to_ingress(
        #     name='xcubehub-cate',
        #     namespace=cate_namespace,
        #     user_id=user_id,
        #     host_uri=host_uri
        # )

        poll_pod_phase(get_pod, namespace=cate_namespace, prefix=user_id)

        try:
            grace = int(grace)
        except ValueError as e:
            raise api.ApiError(500, "Grace wait period must be an integer.")

        time.sleep(int(grace))

        return dict(serverUrl=f'https://{cate_webapi_uri}/{user_id}')
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def get_status(user_id: str):
    cate_namespace = os.environ.get("CATE_WEBAPI_NAMESPACE", "cate")
    pod = get_pod(prefix=user_id + '-cate', namespace=cate_namespace)
    if pod:
        return pod.status.to_dict()
    else:
        return {'phase': 'Unknown'}


def get_pod_count(label_selector: Optional[str] = None):
    cate_namespace = os.environ.get("CATE_WEBAPI_NAMESPACE", "cate")
    ct = count_pods(label_selector=label_selector, namespace=cate_namespace)
    return {'running_pods': ct}
