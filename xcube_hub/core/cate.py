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

from xcube_hub import api, util, poller
from xcube_hub.core import user_namespaces, k8s
from xcube_hub.core.k8s import get_pod
from xcube_hub.typedefs import JsonObject
from xcube_hub.util import maybe_raise_for_invalid_username


def delete_cate(user_id: str, prune: bool = False) -> bool:
    cate_namespace = util.maybe_raise_for_env("WORKSPACE_NAMESPACE", default="cate")

    user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

    deployment = k8s.get_deployment(name=user_id + '-cate', namespace=cate_namespace)

    if deployment:
        k8s.delete_deployment(name=user_id + '-cate', namespace=cate_namespace)

    if prune:
        service_name = user_id + '-cate'
        services = k8s.list_services(namespace=cate_namespace)
        services = [service.metadata.name for service in services.items]
        if service_name in services:
            k8s.delete_service(name=service_name, namespace=cate_namespace)

    return True


def launch_cate(user_id: str) -> JsonObject:
    try:
        max_pods = util.maybe_raise_for_env("CATE_MAX_WEBAPIS", default=50, typ=int)

        grace = util.maybe_raise_for_env("CATE_LAUNCH_GRACE", default=2, typ=int)

        user_id = maybe_raise_for_invalid_username(user_id)

        cate_image = util.maybe_raise_for_env("CATE_IMG")
        cate_tag = util.maybe_raise_for_env("CATE_TAG")
        cate_hash = os.getenv("CATE_HASH", default=None)

        cate_mem_limit = util.maybe_raise_for_env("CATE_MEM_LIMIT", default='16Gi')
        cate_mem_request = util.maybe_raise_for_env("CATE_MEM_REQUEST", default='2Gi')
        cate_webapi_uri = util.maybe_raise_for_env("CATE_WEBAPI_URI")
        cate_use_dapr = os.getenv("CATE_USE_DAPR", None)
        cate_namespace = util.maybe_raise_for_env("WORKSPACE_NAMESPACE", "cate")
        cate_stores_config_path = util.maybe_raise_for_env("CATE_STORES_CONFIG_PATH",
                                                           default="/etc/xcube-hub/stores.yaml")

        # Not used as the namespace cate has to be created prior to launching cate instances
        # user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

        if k8s.count_pods(label_selector="purpose=cate-webapi", namespace=cate_namespace) > max_pods:
            raise api.ApiError(413, "Too many pods running.")

        cate_command = "cate-webapi-start -b -p 4000 -a 0.0.0.0 -r /home/cate/workspace"

        cate_env_activate_command = "source activate cate-env"

        if cate_hash is not None and cate_hash != "null":
            cate_image = cate_image + '@' + cate_hash
        else:
            cate_image = cate_image + ':' + cate_tag

        command = ["/bin/bash", "-c", f"{cate_env_activate_command} && {cate_command}"]

        envs = [client.V1EnvVar(name='CATE_USER_ROOT', value="/home/cate/workspace"),
                client.V1EnvVar(name='CATE_STORES_CONFIG_PATH', value=cate_stores_config_path),
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
                'name': 'xcube-hub-stores',
                'mountPath': '/etc/xcube-hub',
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
                'name': 'xcube-hub-stores',
                'configMap': {
                    'name': 'xcube-hub-stores'
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

        limits = {'memory': cate_mem_limit}
        requests = {'memory': cate_mem_request}

        annotations = {"dapr.io/app-id": user_id + '-cate', "dapr.io/enabled": "true",
                       "dapr.io/log-as-json": "true"} if cate_use_dapr else None

        labels = dict(typ="cate")

        deployment = k8s.create_deployment_object(name=user_id + '-cate',
                                                  application='cate-webapi',
                                                  container_name=user_id + '-cate',
                                                  image=cate_image,
                                                  envs=envs,
                                                  container_port=4000,
                                                  command=command,
                                                  volumes=volumes,
                                                  volume_mounts=volume_mounts,
                                                  init_containers=init_containers,
                                                  limits=limits,
                                                  requests=requests,
                                                  annotations=annotations,
                                                  labels=labels)

        # Make create_if_exists test for broken pods
        # pod_status = get_status(user_id)
        # if pod_status != "Running":
        #     create_deployment(namespace=user_id, deployment=deployment)
        # else:
        k8s.create_deployment_if_not_exists(namespace=cate_namespace, deployment=deployment)

        service = k8s.create_service_object(name=user_id + '-cate', port=4000, target_port=4000)
        k8s.create_service_if_not_exists(service=service, namespace=cate_namespace)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        service_name = user_id + '-cate'

        ingress = k8s.get_ingress(namespace=cate_namespace, name=service_name)
        if not ingress:
            ingress = k8s.create_ingress_object(name=service_name,
                                                service_name=service_name,
                                                service_port=4000,
                                                user_id=user_id,
                                                host_uri=host_uri)
            k8s.create_ingress(ingress, namespace=cate_namespace)

        # add_cate_path_to_ingress(
        #     name='xcubehub-cate',
        #     namespace=cate_namespace,
        #     user_id=user_id,
        #     host_uri=host_uri
        # )

        poller.poll_pod_phase(get_pod, namespace=cate_namespace, prefix=user_id)

        try:
            grace = int(grace)
        except ValueError as e:
            raise api.ApiError(400, "Grace wait period must be an integer.")

        time.sleep(int(grace))

        return dict(serverUrl=f'https://{cate_webapi_uri}/{user_id}')
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def get_status(user_id: str):
    user_id = maybe_raise_for_invalid_username(user_id)

    cate_namespace = os.environ.get("WORKSPACE_NAMESPACE", "cate")
    pod = k8s.get_pod(prefix=user_id + '-cate', namespace=cate_namespace)
    if pod:
        return pod.status.to_dict()
    else:
        return {'phase': 'Unknown'}


def get_pod_count(label_selector: Optional[str] = None):
    cate_namespace = os.environ.get("WORKSPACE_NAMESPACE", "cate")
    ct = k8s.count_pods(label_selector=label_selector, namespace=cate_namespace)
    return {'running_pods': ct}
