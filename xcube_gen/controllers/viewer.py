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
from kubernetes import client
from kubernetes.client.rest import ApiException

from xcube_gen import api
from xcube_gen.k8s import create_deployment, create_deployment_object, create_service_object, create_service, \
    create_xcube_serve_ingress_object, create_xcube_genserv_ingress, delete_deployment, delete_service, delete_ingress, \
    list_ingress, list_service
from xcube_gen.xg_types import JsonObject


def launch_viewer(user_id: str, output_config: JsonObject) -> JsonObject:
    try:
        apps_v1_api = client.AppsV1Api()
        deployments = apps_v1_api.list_namespaced_deployment(namespace=user_id)
        deployments = [deployment.metadata.name for deployment in deployments.items]
        if len(deployments) > 0:
            delete_deployment(api_instance=apps_v1_api, name=user_id, namespace=user_id)
            delete_service(name=user_id, namespace=user_id)

        services = list_service(name=user_id, namespace=user_id)
        services = [service.metadata.name for service in services.items]
        if len(services) > 0:
            delete_service(name=user_id, namespace=user_id)

        ingresses = list_ingress(namespace=user_id)
        ingresses = [ingress.metadata.name for ingress in ingresses.items]
        if len(ingresses) > 0:
            delete_ingress(name=user_id, namespace=user_id)
        import time
        time.sleep(20)

        deployment = create_deployment_object(name=user_id, container_name=user_id,
                                              image='quay.io/bcdev/xcube-webapi:0.5.0.dev2',
                                              container_port=4000,
                                              config=output_config)

        create_deployment(api_instance=apps_v1_api, deployment=deployment, namespace=user_id)

        service = create_service_object(name=user_id, port=4000, target_port=4000)
        create_service(service=service, namespace=user_id)

        ingress = create_xcube_serve_ingress_object(name=user_id, service_name=user_id, service_port=4000,
                                                    user_id=user_id)
        create_xcube_genserv_ingress(ingress, namespace=user_id)
        time.sleep(20)

    except ApiException as e:
        raise api.ApiError(e.status, str(e))

    return dict(viewerUri='https://xcube-gen.brockmann-consult.de/viewer',
                serverUri=f'https://xcube-gen.brockmann-consult.de/{user_id}')