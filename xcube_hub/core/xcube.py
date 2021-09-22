import json
import os
import uuid
from typing import Tuple

from kubernetes import client
from kubernetes.client import ApiException, V1EnvVarSource, V1SecretKeySelector
from polling2 import TimeoutException, MaxCallException
from urllib3.exceptions import MaxRetryError

from xcube_hub import api, util, poller
from xcube_hub.core import k8s
from xcube_hub.typedefs import JsonObject


def _create_xcube_deployment_object(user_id: str, cfg_id: str, cfg: JsonObject) -> client.V1Deployment:
    xcube_cfg_root_dir = util.maybe_raise_for_env("XCUBE_CFG_ROOT_DIR")
    if not os.path.isdir(xcube_cfg_root_dir):
        os.mkdir(xcube_cfg_root_dir)

    cfg_file_name = os.path.join(xcube_cfg_root_dir, cfg_id + ".json")

    with open(cfg_file_name, "w") as f:
        json.dump(cfg, f)

    xcube_repo = util.maybe_raise_for_env("XCUBE_REPO")
    xcube_tag = util.maybe_raise_for_env("XCUBE_TAG")
    xcube_hash = os.getenv("XCUBE_HASH", default=None)

    if xcube_hash is not None and xcube_hash != "null":
        image = xcube_repo + '@' + xcube_hash
    else:
        image = xcube_repo + ':' + xcube_tag

    cmd = "source activate xcube && xcube serve -v --traceperf -P 8080 -A 0.0.0.0 -c " + \
          cfg_file_name

    cmd = ["/bin/bash", "-c", cmd]

    secret_name = "xcube-hub-secrets"

    envs = [
        client.V1EnvVar(name="SH_CLIENT_ID", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="SH_CLIENT_ID"
            ))),
        client.V1EnvVar(name="SH_CLIENT_SECRET", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="SH_CLIENT_SECRET"
            ))),
        client.V1EnvVar(name="SH_INSTANCE_ID", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="SH_INSTANCE_ID"
            ))),
        client.V1EnvVar(name="CDSAPI_URL", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="CDSAPI_URL"
            ))),
        client.V1EnvVar(name="CDSAPI_KEY", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="CDSAPI_KEY"
            ))),
        client.V1EnvVar(name="AWS_ACCESS_KEY_ID", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="AWS_ACCESS_KEY_ID"
            ))),
        client.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key="AWS_SECRET_ACCESS_KEY"
            )))
    ]

    volume_mounts = [
        {
            'name': 'workspace-pvc',
            'mountPath': '/data',
        },
    ]

    volumes = [
        {
            'name': 'workspace-pvc',
            'persistentVolumeClaim': {
                'claimName': 'workspace-pvc',
            }
        },
    ]

    deployment = k8s.create_deployment_object(name=user_id,
                                              user_id=user_id,
                                              container_name=user_id,
                                              image=image,
                                              container_port=8080,
                                              command=cmd,
                                              envs=envs,
                                              volume_mounts=volume_mounts,
                                              volumes=volumes,
                                              limits={},
                                              requests={})

    return deployment


def create(user_id: str, cfg: JsonObject) -> Tuple[JsonObject, int]:
    try:
        cfg_id = f"{user_id}-{str(uuid.uuid4())[:18]}"

        xcube_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")

        try:
            k8s.delete_deployment(name=user_id, namespace=xcube_namespace)
            import time
            time.sleep(10)
            k8s.delete_service(name=user_id, namespace=xcube_namespace)
            k8s.delete_ingress(name=user_id, namespace=xcube_namespace)
        except api.ApiError as e:
            print("Warning:", str(e))
            pass

        # Create deployment
        deployment = _create_xcube_deployment_object(user_id=user_id, cfg_id=cfg_id, cfg=cfg)
        k8s.create_deployment(namespace=xcube_namespace, deployment=deployment)

        try:
            poller.poll_pod_phase(k8s.get_pod, namespace=xcube_namespace, prefix=user_id)
        except (TimeoutException, MaxCallException) as e:
            raise api.ApiError(408, str(e))

        # Create service
        service = k8s.create_service_object(name=user_id, port=8080, target_port=8080)
        k8s.create_service(service=service, namespace=xcube_namespace)

        # Create ingress

        host_uri = os.environ.get("XCUBE_WEBAPI_URI")
        viewer_uri = os.environ.get("XCUBE_VIEWER_URI")
        annotations = {
            "nginx.ingress.kubernetes.io/proxy-connect-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-read-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-send-timeout": "86400",
            "nginx.ingress.kubernetes.io/send-timeout": "86400",
            "nginx.ingress.kubernetes.io/proxy-body-size": "2000m",
            "nginx.ingress.kubernetes.io/enable-cors": "true",
            "nginx.ingress.kubernetes.io/rewrite-target": "/$1"
        }

        ingress = k8s.create_ingress_object(name=user_id,
                                            service_name=user_id,
                                            service_port=8080,
                                            user_id=user_id,
                                            host_uri=host_uri,
                                            annotations=annotations)

        k8s.create_ingress(ingress, namespace=xcube_namespace)
        server_url = f"{host_uri}/{user_id}/"
        viewer_url = f"{viewer_uri}?serverUrl={server_url}&serverName={user_id}"

        return {
                   'server_url': server_url,
                   'viewer_url': viewer_url
               }, 200
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, message=str(e))
    except Exception as e:
        raise api.ApiError(400, message=str(e))


def delete(user_id: str):
    xcube_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
    k8s.delete_deployment(name=user_id, namespace=xcube_namespace)
    return "SUCCESS"
