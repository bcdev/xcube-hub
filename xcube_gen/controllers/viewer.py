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

from xcube_gen import api
from xcube_gen.controllers import user_namespaces
from xcube_gen.k8s import create_deployment, create_deployment_object, create_service_object, create_service, \
    create_ingress_object, create_ingress, delete_deployment, delete_service, delete_ingress, \
    list_ingress, list_service, get_pod
from xcube_gen.poller import poll_deployment_status, poll_pod_phase
from xcube_gen.typedefs import JsonObject


def launch_viewer(user_id: str, output_config: JsonObject) -> JsonObject:
    try:
        user_namespaces.create_if_not_exists(user_id=user_id)

        xcube_image = os.environ.get("XCUBE_DOCKER_WEBAPI_IMG")
        xcube_webapi_uri = os.environ.get("XCUBE_WEBAPI_URI")
        xcube_viewer_path = os.environ.get("XCUBE_VIEWER_PATH") or '/viewer'

        if not xcube_image:
            raise api.ApiError(400, "Could not find the xcube docker image.")

        if not xcube_webapi_uri:
            raise api.ApiError(400, "Could not find the xcube webapi uri.")

        apps_v1_api = client.AppsV1Api()
        deployments = apps_v1_api.list_namespaced_deployment(namespace=user_id)
        deployments = [deployment.metadata.name for deployment in deployments.items]
        if len(deployments) > 0:
            delete_deployment(name=user_id, namespace=user_id)
            delete_service(name=user_id, namespace=user_id)

        services = list_service(name=user_id, namespace=user_id)
        services = [service.metadata.name for service in services.items]
        if len(services) > 0:
            delete_service(name=user_id, namespace=user_id)

        ingresses = list_ingress(namespace=user_id)
        ingresses = [ingress.metadata.name for ingress in ingresses.items]
        if len(ingresses) > 0:
            delete_ingress(name=user_id, namespace=user_id)

        poll_deployment_status(apps_v1_api.list_namespaced_deployment, status='empty', namespace=user_id)

        envs = [
            client.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=output_config.get('secretAccessKey')),
            client.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=output_config.get('accessKeyId')),
        ]

        bucket_url = "https://s3.amazonaws.com/" + output_config.get('bucketUrl') + '/' + output_config.get(
            'dataId') + '.zarr'

        command = ["bash", "-c",
                   f"source activate xcube && xcube serve --traceperf -v --prefix {user_id} --aws-env "
                   f"-P 4000 -A 0.0.0.0 "
                   f"{bucket_url}"]

        deployment = create_deployment_object(name=user_id,
                                              user_id=user_id,
                                              container_name=user_id,
                                              image=xcube_image,
                                              container_port=4000,
                                              envs=envs,
                                              command=command)

        create_deployment(deployment=deployment, namespace=user_id)

        service = create_service_object(name=user_id, port=4000, target_port=4000)
        create_service(service=service, namespace=user_id)

        host_uri = os.environ.get("XCUBE_WEBAPI_URI")
        ingress = create_ingress_object(name=user_id,
                                        service_name=user_id,
                                        service_port=4000,
                                        user_id=user_id,
                                        host_uri=host_uri)
        create_ingress(ingress, namespace=user_id)

        # poll_deployment_status(apps_v1_api.read_namespaced_deployment, status='ready', namespace=user_id, name=user_id)
        poll_pod_phase(get_pod, namespace=user_id, prefix=user_id)

        grace = os.environ.get("CATE_LAUNCH_GRACE", False) or 2
        time.sleep(grace)

        return dict(viewerUri=f'{xcube_webapi_uri}{xcube_viewer_path}',
                    serverUri=f'{xcube_webapi_uri}/{user_id}')
    except ApiException as e:
        raise api.ApiError(e.status, str(e))


def get_status(user_id: str):
    pod = get_pod(prefix=user_id, namespace=user_id)
    if pod:
        return pod.status.to_dict()
    else:
        raise api.ApiError(404, f'No  xcube-gen-ui Pod for user {user_id}')
