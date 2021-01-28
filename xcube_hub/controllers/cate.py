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

from xcube_hub import api
from xcube_hub.controllers import user_namespaces
from xcube_hub.k8s import create_deployment_object, create_service_object, \
    delete_deployment, delete_service, list_services, get_pod, \
    create_deployment_if_not_exists, create_service_if_not_exists, count_pods, \
    add_cate_path_to_ingress, get_deployment
from xcube_hub.poller import poll_pod_phase
from xcube_hub.typedefs import JsonObject
from xcube_hub.utilities import raise_for_invalid_username, load_env_by_regex


def delete_cate(user_id: str, prune: bool = False) -> bool:
    cate_namespace = os.environ.get("CATE_WEBAPI_NAMESPACE", "cate-userspace")

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

        # ingresses = list_ingress(namespace=cate_namespace)
        # ingresses = [ingress.metadata.name for ingress in ingresses.items]
        # if len(ingresses) > 0:
        #     delete_ingress(name=user_id + '-cate', namespace=cate_namespace)

    return True


def launch_cate(user_id: str) -> JsonObject:
    try:
        max_pods = 50

        grace = os.environ.get("CATE_LAUNCH_GRACE", 2)

        raise_for_invalid_username(user_id)

        if count_pods(label_selector="purpose=cate-webapi") > max_pods:
            raise api.ApiError(410, "Too many pods running.")

        cate_user_root = os.environ.get("CATE_USER_ROOT", "/home/cate/workspace")

        cate_envs = [client.V1EnvVar(name='CATE_USER_ROOT', value=cate_user_root),
                     client.V1EnvVar(name='JUPYTERHUB_SERVICE_PREFIX', value='/' + user_id + '/')]

        cate_envs += load_env_by_regex(r"^AWS_")
        cate_envs += load_env_by_regex(r"^CATE_WEBAPI_")

        cate_image = os.environ.get("CATE_IMG")
        cate_version = os.environ.get("CATE_VERSION")
        cate_command = os.environ.get("CATE_COMMAND", False)
        cate_obs_name = os.environ.get("CATE_OBS_NAME", "mnt-goofys")
        cate_env_activate_command = os.environ.get("CATE_ENV_ACTIVATE_COMMAND", False)
        cate_webapi_uri = os.environ.get("CATE_WEBAPI_URI")
        cate_namespace = os.environ.get("CATE_WEBAPI_NAMESPACE", "cate-userspace")
        cate_workspace_claim_name = os.environ.get("CATE_WORKSPACE_CLAIM_NAME", "workspace-pvc")

        user_namespaces.create_if_not_exists(user_namespace=cate_namespace)

        if not cate_command:
            cate_command = "cate-webapi-start -b -p 4000 -a 0.0.0.0 -r /home/cate/workspace"

        if not cate_env_activate_command:
            cate_env_activate_command = "source activate cate-env"

        if not cate_image:
            raise api.ApiError(400, "Could not find the cate webapi docker image.")

        cate_image = cate_image + ':' + cate_version

        command = ["/bin/bash", "-c", f"{cate_env_activate_command} && {cate_command}"]

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
                'mountPath': "/home/cate/storage",
                'name': cate_obs_name,
            }]

        volumes = [
            {
                'name': cate_obs_name,
                'hostPath': {
                    'path': '/var/s3'
                }
            },
            {
                'name': 'workspace-pvc',
                'persistentVolumeClaim': {
                    'claimName': cate_workspace_claim_name,
                }
            }]

        deployment = create_deployment_object(name=user_id + '-cate',
                                              user_id=user_id,
                                              container_name=user_id + '-cate',
                                              image=cate_image,
                                              envs=cate_envs,
                                              container_port=4000,
                                              command=command,
                                              volumes=volumes,
                                              volume_mounts=volume_mounts)

        # TODO: Make create_if_exists test for broken pods
        # pod_status = get_status(user_id)
        # if pod_status != "Running":
        #     create_deployment(namespace=user_id, deployment=deployment)
        # else:
        create_deployment_if_not_exists(namespace=cate_namespace, deployment=deployment)

        service = create_service_object(name=user_id + '-cate', port=4000, target_port=4000)
        create_service_if_not_exists(service=service, namespace=cate_namespace)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        add_cate_path_to_ingress(
            name='xcubehub-ingress',
            namespace=cate_namespace,
            user_id=user_id,
            host_uri=host_uri
        )

        poll_pod_phase(get_pod, namespace=cate_namespace, prefix=user_id)

        try:
            grace = int(grace)
        except ValueError as e:
            raise api.ApiError(500, "Grace wait period must be an integer.")

        time.sleep(int(grace))

        return dict(serverUrl=f'{cate_webapi_uri}/{user_id}')
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
    ct = count_pods(label_selector=label_selector)
    return {'running_pods': ct}
