import os
import time
from typing import Dict

from kubernetes.client import ApiException

from xcube_hub import util, api
from xcube_hub.core import user_namespaces
from xcube_hub.core.k8s import count_pods, create_deployment_object, create_deployment_if_not_exists, \
    create_service_object, create_service_if_not_exists, get_ingress, create_ingress_object, create_ingress, get_pod
from xcube_hub.models.subscription import Subscription
from xcube_hub.poller import poll_pod_phase
from xcube_hub.typedefs import JsonObject


def register(user_id: str, subscription: Subscription, headers: Dict, raising: bool = True):

    return True


def launch_geoserver(user_id: str) -> JsonObject:
    try:
        xcube_geoserver_namespace = "xc_geoserv"
        max_pods = util.maybe_raise_for_env("XCUBE_GEOSERVER_MAX_WEBAPIS", default=50, typ=int)

        grace = util.maybe_raise_for_env("XCUBE_GEOSERVER_LAUNCH_GRACE", default=2, typ=int)

        util.raise_for_invalid_username(user_id)

        if count_pods(label_selector="purpose=geoserver") > max_pods:
            raise api.ApiError(413, "Too many pods running.")

        xcube_geoserv_image = os.environ.get("XCUBE_GEOSERVER_IMG")
        xcube_geoserv_version = os.environ.get("XCUBE_GEOSERVER_VERSION")

        user_namespaces.create_if_not_exists(user_namespace=xcube_geoserver_namespace)

        if not xcube_geoserv_image:
            raise api.ApiError(400, "Could not find the cate webapi docker image.")

        xcube_geoserv_image = xcube_geoserv_image + ':' + xcube_geoserv_version

        # envs = [client.V1EnvVar(name='CATE_USER_ROOT', value="/home/cate/workspace"),
        #         client.V1EnvVar(name='CATE_STORES_CONFIG_PATH', value="/etc/cate/stores.yaml"),
        #         client.V1EnvVar(name='JUPYTERHUB_SERVICE_PREFIX', value='/' + user_id + '/')]

        # volume_mounts = [
        #     {
        #         'name': 'workspace-pvc',
        #         'mountPath': '/home/cate/workspace',
        #         'subPath': user_id + '-scratch'
        #     },
        #     {
        #         'name': 'workspace-pvc',
        #         'mountPath': '/home/cate/.cate',
        #         'subPath': user_id + '-cate'
        #     },
        #     {
        #         'name': 'cate-stores',
        #         'mountPath': '/etc/cate',
        #         'readOnly': True
        #     },
        # ]
        #
        # volumes = [
        #     {
        #         'name': 'workspace-pvc',
        #         'persistentVolumeClaim': {
        #             'claimName': 'workspace-pvc',
        #         }
        #     },
        #     {
        #         'name': 'cate-stores',
        #         'configMap': {
        #             'name': 'cate-stores'
        #         }
        #     },
        # ]

        deployment = create_deployment_object(name=user_id + '-geoserv',
                                              user_id=user_id,
                                              container_name=user_id + '-geoserv',
                                              image=xcube_geoserv_image,
                                              container_port=8080)

        # Make create_if_exists test for broken pods
        # pod_status = get_status(user_id)
        # if pod_status != "Running":
        #     create_deployment(namespace=user_id, deployment=deployment)
        # else:
        create_deployment_if_not_exists(namespace=xcube_geoserver_namespace, deployment=deployment)

        service = create_service_object(name=user_id + '-geoserv', port=8080, target_port=8080)
        create_service_if_not_exists(service=service, namespace=xcube_geoserver_namespace)

        host_uri = os.environ.get("CATE_WEBAPI_URI")

        service_name = user_id + '-geoserv'

        ingress = get_ingress(namespace=xcube_geoserver_namespace, name=service_name)

        if not ingress:
            ingress = create_ingress_object(name=service_name,
                                            service_name=service_name,
                                            service_port=4000,
                                            user_id=user_id,
                                            host_uri=host_uri)
            create_ingress(ingress, namespace=xcube_geoserver_namespace)

        poll_pod_phase(get_pod, namespace=xcube_geoserver_namespace, prefix=user_id)

        try:
            grace = int(grace)
        except ValueError as e:
            raise api.ApiError(500, "Grace wait period must be an integer.")

        time.sleep(int(grace))

        xcube_geoserv_webapi_uri = util.maybe_raise_for_env("XCUBE_GEOSERVER_WEBAPI_URI")

        return dict(serverUrl=f'https://{xcube_geoserv_webapi_uri}/{user_id}')
    except ApiException as e:
        raise api.ApiError(e.status, str(e))
