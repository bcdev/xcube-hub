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

from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_hub import api, util, poller
from xcube_hub.core import user_namespaces, k8s
from xcube_hub.core.k8s import get_pod
from xcube_hub.typedefs import JsonObject
from xcube_hub.util import maybe_raise_for_invalid_username


def delete_cate(user_id: str, prune: bool = False) -> bool:
    cate_namespace = util.maybe_raise_for_env("WORKSPACE_NAMESPACE",
                                              default="cate")

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

        cate_image = util.maybe_raise_for_env("CATE_IMG", default='quay.io/ccitools/cate')
        cate_tag = util.maybe_raise_for_env("CATE_TAG", default='2.1.5')
        cate_hash = os.getenv("CATE_HASH", default=None)
        cate_debug = os.getenv("CATE_DEBUG", default='0')
        cate_launch_grace = os.getenv("CATE_LAUNCH_GRACE_PERIOD", default=2)

        cate_mem_limit = util.maybe_raise_for_env("CATE_MEM_LIMIT", default='16Gi')
        cate_mem_request = util.maybe_raise_for_env("CATE_MEM_REQUEST", default='2Gi')
        cate_webapi_uri = util.maybe_raise_for_env("CATE_WEBAPI_URI", default='dev.catehub.climate.esa.int')
        cate_namespace = util.maybe_raise_for_env("WORKSPACE_NAMESPACE", "cate")
        cate_stores_config_path = util.maybe_raise_for_env("CATE_STORES_CONFIG_PATH",
                                                           default="/etc/xcube-hub/stores.yaml")
        cate_user_root = util.maybe_raise_for_env("CATE_USER_ROOT",
                                                  "/home/xcube/workspace")

        cate_command = util.maybe_raise_for_env("CATE_COMMAND",
                                                "cate-webapi-start -v -b -p 4000 "
                                                "-a 0.0.0.0 -s 86400 -r"
                                                f"{cate_user_root}")


        cate_storage_mode = util.maybe_raise_for_env("CATE_STORAGE_MODE", "pvc")

        # Not used as the namespace cate has to be created prior to launching cate instances
        # user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

        if get_pod_count().get('running_pods', 0) > max_pods:
            raise api.ApiError(413, "Too many pods running.")

        cate_env_activate_command = "source activate xcube"

        if cate_hash is not None and cate_hash != "null":
            cate_image = cate_image + '@' + cate_hash
        else:
            cate_image = cate_image + ':' + cate_tag

        command = ["/bin/bash", "-c", f"{cate_env_activate_command} && {cate_command}"]

        envs = [client.V1EnvVar(name='CATE_USER_ROOT',
                                value=cate_user_root),
                client.V1EnvVar(name='CATE_DEBUG',
                                value=cate_debug),
                client.V1EnvVar(name='CATE_STORES_CONFIG_PATH',
                                value=cate_stores_config_path),
                client.V1EnvVar(name='JUPYTERHUB_SERVICE_PREFIX',
                                value=f'/{user_id}/'),
                client.V1EnvVar(name='CATE_NODE_NAME',
                                value_from=client.V1EnvVarSource(
                                    field_ref=client.V1ObjectFieldSelector(
                                        field_path='spec.nodeName'
                                    )
                                )
                )
                ]

        volume_mounts = None
        volumes = None
        init_containers = None
        if cate_storage_mode == "pvc":
            volume_mounts = [
                {
                    'name': 'workspace-pvc',
                    'mountPath': '/home/xcube/workspace',
                    'subPath': user_id + '-scratch'
                },
                {
                    'name': 'workspace-pvc',
                    'mountPath': '/home/xcube/.cate',
                    'subPath': user_id + '-cate'
                },
                {
                    'name': 'workspace-pvc',
                    'mountPath': '/etc/logs',
                    'subPath': 'logs'
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
                    "image": "quay.io/bcdev/bash:latest",
                    "command": ["chown",
                                "-R",
                                "1000.1000",
                                "/home/xcube/.cate",
                                "etc/logs",
                                "/home/xcube/workspace"],
                    "volumeMounts": [
                        {
                            "mountPath": "/home/xcube/.cate",
                            "subPath": user_id + '-cate',
                            "name": "workspace-pvc",
                        },
                        {
                            "mountPath": '/etc/logs',
                            "subPath": 'logs',
                            "name": "workspace-pvc",
                        },
                        {
                            "mountPath": "/home/xcube/workspace",
                            "subPath": user_id + '-scratch',
                            "name": "workspace-pvc",
                        },
                    ]
                },
            ]

        limits = {'memory': cate_mem_limit}
        requests = {'memory': cate_mem_request}

        labels = dict(typ="cate")

        lifecycle_handler_command = \
            'echo $(date +"%Y-%m-%d-%T"),'\
            '$JUPYTERHUB_SERVICE_PREFIX,'\
            '$CATE_NODE_NAME,'\
            '{},'\
            '$(cat /proc/$(pgrep cate-webapi-sta)/oom_score),'\
            '$(cat /proc/$(pgrep cate-webapi-sta)/oom_score_adj),'\
            '$(cat /proc/$(pgrep cate-webapi-sta)/status | grep State),'\
            '$(dmesg | tail -3) >> /etc/logs/logs.csv'

        lifecycle = client.V1Lifecycle(
            post_start=client.V1LifecycleHandler(
                _exec=client.V1ExecAction(
                    command=["/bin/sh", "-c",
                             lifecycle_handler_command.format('start')]
                )
            ),
            pre_stop=client.V1LifecycleHandler(
                _exec=client.V1ExecAction(
                    command=["/bin/sh", "-c",
                             lifecycle_handler_command.format('stop')]
                )
            )
        )

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
                                                  labels=labels,
                                                  lifecycle=lifecycle)

        # delete previous cate deployment to make sure pod is not restarted
        delete_cate(user_id, prune=True)

        while k8s.get_deployment(name=user_id + '-cate', namespace=cate_namespace):
            # do not create the new deployment while the old one is still there
            time.sleep(0.1)

        k8s.create_deployment(namespace=cate_namespace, deployment=deployment)

        time.sleep(cate_launch_grace)

        service = k8s.create_service_object(name=user_id + '-cate', port=4000, target_port=4000)
        k8s.create_service_if_not_exists(service=service, namespace=cate_namespace)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        service_name = user_id + '-cate'

        annotations = {
            "proxy_set_header": "Upgrade $http_upgrade; Connection \"upgrade\"",
            "nginx.ingress.kubernetes.io/proxy-connect-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-read-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-send-timeout": "86400",
            "nginx.ingress.kubernetes.io/send-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-body-size": "2000m",
            "nginx.ingress.kubernetes.io/enable-cors": "true",
            "kubernetes.io/ingress.class": "nginx",
            "nginx.ingress.kubernetes.io/websocket-services": service_name
        }

        ingress = k8s.get_ingress(namespace=cate_namespace, name=service_name)
        if not ingress:
            ingress = k8s.create_ingress_object(name=service_name,
                                                service_name=service_name,
                                                service_port=4000,
                                                user_id=user_id,
                                                annotations=annotations,
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


def get_pod_count():
    cate_namespace = os.environ.get("WORKSPACE_NAMESPACE", "cate")
    label_selector = 'application=cate-webapi'
    ct = k8s.count_pods(label_selector=label_selector, namespace=cate_namespace)
    return {'running_pods': ct}
