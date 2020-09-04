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

from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api
from xcube_gen.controllers import user_namespaces
from xcube_gen.k8s import create_deployment_object, create_service_object, \
    create_ingress_object, delete_deployment, delete_service, delete_ingress, \
    list_ingress, list_service, get_pod, create_pvc_object, create_pvc_if_not_exists, create_deployment_if_not_exists, \
    create_service_if_not_exists, create_ingress_if_not_exists
from xcube_gen.poller import poll_pod_phase
from xcube_gen.typedefs import JsonObject


def delete_cate(user_id: str, prune: bool = False) -> bool:
    user_namespaces.create_if_not_exists(user_id=user_id)

    if prune:
        core_v1_api = client.CoreV1Api()
        pvcs = core_v1_api.list_namespaced_persistent_volume_claim(namespace=user_id)
        pvcs = [pvc.metadata.name for pvc in pvcs.items]
        if len(pvcs) == 0:
            core_v1_api.delete_collection_namespaced_persistent_volume_claim(namespace=user_id)

    apps_v1_api = client.AppsV1Api()

    deployments = apps_v1_api.list_namespaced_deployment(namespace=user_id)
    deployments = [deployment.metadata.name for deployment in deployments.items]
    if len(deployments) > 0:
        delete_deployment(name=user_id + '-cate', namespace=user_id)

    if prune:
        services = list_service(name=user_id + '-cate', namespace=user_id)
        services = [service.metadata.name for service in services.items]
        if len(services) > 0:
            delete_service(name=user_id + '-cate', namespace=user_id)

        ingresses = list_ingress(namespace=user_id)
        ingresses = [ingress.metadata.name for ingress in ingresses.items]
        if len(ingresses) > 0:
            delete_ingress(name=user_id + '-cate', namespace=user_id)

    return True


def launch_cate(user_id: str, output_config: JsonObject) -> JsonObject:
    try:
        user_namespaces.create_if_not_exists(user_id=user_id)

        cate_image = os.environ.get("CATE_WEBAPI_IMG")
        cate_webapi_uri = os.environ.get("CATE_WEBAPI_URI")

        if not cate_image:
            raise api.ApiError(400, "Could not find the cate webapi docker image.")

        pvc = create_pvc_object(user_id)
        create_pvc_if_not_exists(pvc, user_id)

        command = ["/bin/bash", "-c", "echo 'Hello' && source activate cate-env && cate-webapi-start "
                                      "-b -v -p 4000 -a 0.0.0.0"]

        deployment = create_deployment_object(name=user_id + '-cate',
                                              user_id=user_id,
                                              container_name=user_id + '-cate',
                                              image=cate_image,
                                              container_port=4000,
                                              command=command)

        create_deployment_if_not_exists(user_id, deployment)

        service = create_service_object(name=user_id + '-cate', port=4000, target_port=4000)
        create_service_if_not_exists(service=service, namespace=user_id)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        ingress = create_ingress_object(name=user_id + '-cate',
                                        service_name=user_id + '-cate',
                                        service_port=4000,
                                        user_id=user_id,
                                        host_uri=host_uri)

        create_ingress_if_not_exists(ingress, namespace=user_id)

        poll_pod_phase(get_pod, namespace=user_id, prefix=user_id)

        return dict(serverUri=f'{cate_webapi_uri}/{user_id}')
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def get_status(user_id: str):
    pod = get_pod(prefix=user_id + '-cate', namespace=user_id)
    if pod:
        return pod.status.to_dict()
    else:
        raise api.ApiError(404, f'No cate Pod for user {user_id}')
