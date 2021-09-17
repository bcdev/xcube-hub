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


def _create_xcube_deployment_object(user_id: str, pod_id: str, cfg: JsonObject) -> client.V1Deployment:
    xcube_cfg_root_dir = util.maybe_raise_for_env("XCUBE_CFG_ROOT_DIR")
    if not os.path.isdir(xcube_cfg_root_dir):
        os.mkdir(xcube_cfg_root_dir)

    cfg_file_name = os.path.join(xcube_cfg_root_dir, pod_id + ".json")

    with open(cfg_file_name, "w") as f:
        json.dump(cfg, f)

    xcube_repo = util.maybe_raise_for_env("XCUBE_REPO")
    xcube_tag = util.maybe_raise_for_env("XCUBE_TAG")
    xcube_hash = os.getenv("XCUBE_HASH", default=None)

    if xcube_hash is not None and xcube_hash != "null":
        image = xcube_repo + '@' + xcube_hash
    else:
        image = xcube_repo + ':' + xcube_tag

    cmd = f"source activate xcube && xcube serve -v -P 8080 -A 0.0.0.0 --prefix=/api -c {cfg_file_name}"

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

    deployment = k8s.create_deployment_object(name=pod_id,
                                              user_id=user_id,
                                              container_name=pod_id,
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
        pod_id = f"{user_id}-{str(uuid.uuid4())[:18]}"

        xcube_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")

        # Create deployment
        deployment = _create_xcube_deployment_object(user_id=user_id, pod_id=pod_id, cfg=cfg)
        k8s.create_deployment_if_not_exists(namespace=xcube_namespace, deployment=deployment)

        try:
            poller.poll_pod_phase(k8s.get_pod, namespace=xcube_namespace, prefix=user_id)
        except (TimeoutException, MaxCallException) as e:
            raise api.ApiError(408, str(e))

        # Create service
        service = k8s.create_service_object(name=user_id + '-xcube', port=8080, target_port=8080)
        k8s.create_service_if_not_exists(service=service, namespace=xcube_namespace)

        # Create ingress

        host_uri = os.environ.get("XCUBE_WEBAPI_URI")

        service_name = user_id + '-xcube'

        ingress = k8s.get_ingress(namespace=xcube_namespace, name=service_name)
        if not ingress:
            ingress = k8s.create_ingress_object(name=service_name,
                                                service_name=service_name,
                                                service_port=8080,
                                                user_id=user_id,
                                                host_uri=host_uri)

            k8s.create_ingress(ingress, namespace=xcube_namespace)
        return {'pod_id': pod_id}, 200
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, message=str(e))
    except Exception as e:
        raise api.ApiError(400, message=str(e))


def delete():
    return "SUCCESS"
