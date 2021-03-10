import json
import os
import uuid
from pprint import pprint
from typing import Union, Sequence, Optional

import yaml
from kubernetes import client
from kubernetes.client import ApiException
from urllib3.exceptions import MaxRetryError

from xcube_hub import api, poller
from xcube_hub.api import get_json_request_value
from xcube_hub.auth import Auth
from xcube_hub.core import callbacks, costs, punits
from xcube_hub.core import user_namespaces
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.typedefs import AnyDict, Error, JsonObject


def get(user_id: str, cubegen_id: str) -> Union[AnyDict, Error]:
    try:
        output = logs(job_id=cubegen_id)
        stat = status(job_id=cubegen_id)

        progress = callbacks.get_callback(user_id=user_id, cubegen_id=cubegen_id)

        if not stat:
            raise api.ApiError(404, message=f"Cubegen {cubegen_id} not found")

        return {'cubegen_id': cubegen_id, 'status': stat, 'output': output, 'progress': progress}
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def create_cubegen_object(cubegen_id: str, cfg: AnyDict, info_only: bool = False) -> client.V1Job:
    # Configure Pod template container
    sh_client_id = os.environ.get("SH_CLIENT_ID")
    sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
    sh_instance_id = os.environ.get("SH_INSTANCE_ID")
    gen_image = os.environ.get("XCUBE_DOCKER_IMG")
    gen_container_pull_policy = os.environ.get("XCUBE_GEN_DOCKER_PULL_POLICY")
    cdsapi_url = os.getenv("CDSAPI_URL")
    cdsapi_key = os.getenv("CDSAPI_KEY")

    if not gen_image:
        raise api.ApiError(400, "Could not find any xcube-sh docker image.")

    if not sh_client_secret or not sh_client_id or not sh_instance_id:
        raise api.ApiError(400, "SentinelHub credentials invalid. Please contact Brockmann Consult")

    if not cfg:
        raise api.ApiError(400, "create_gen_cubegen_object needs a config dict.")

    info_flag = " -i " if info_only else ""

    cmd = ["/bin/bash", "-c", f"source activate xcube && echo \'{json.dumps(cfg)}\' "
                              f"| xcube --traceback gen2 {info_flag} -v --stores /etc/xcube/data-pools.yaml"]

    sh_envs = [
        client.V1EnvVar(name="SH_CLIENT_ID", value=sh_client_id),
        client.V1EnvVar(name="SH_CLIENT_SECRET", value=sh_client_secret),
        client.V1EnvVar(name="SH_INSTANCE_ID", value=sh_instance_id),
        client.V1EnvVar(name="CDSAPI_URL", value=cdsapi_url),
        client.V1EnvVar(name="CDSAPI_KEY", value=cdsapi_key),
    ]

    volume_mounts = [
        {
            'name': 'xcube-datapools',
            'mountPath': '/etc/xcube',
            'readOnly': True
        }, ]

    volumes = [
        {
            'name': 'xcube-datapools',
            'configMap': {
                'name': 'xcube-datapools'
            }
        }, ]

    container = client.V1Container(
        name="xcube-gen",
        image=gen_image,
        command=cmd,
        volume_mounts=volume_mounts,
        image_pull_policy=gen_container_pull_policy,
        env=sh_envs)
    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "xcube-gen"}),
        spec=client.V1PodSpec(
            volumes=volumes,
            restart_policy="Never",
            containers=[container]
        ))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=1)
    # Instantiate the cubegen object
    cubegen = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=cubegen_id),
        spec=spec)

    return cubegen


def _raise_for_invalid_punits(user_id: str, email: str, cfg: AnyDict, token: str):
    limit = os.getenv("XCUBE_HUB_PROCESS_LIMIT", 1000)

    infos = info(user_id=user_id, email=email, body=cfg, token=token)
    cost_estimation = infos['cost_estimation']

    if cost_estimation['required'] > int(limit):
        raise api.ApiError(400, f"Number of required punits ({cost_estimation['required']}) is greater than the absolute limit of {limit}")

    if cost_estimation['required'] > cost_estimation['available']:
        raise api.ApiError(400, f"Number of required punits ({cost_estimation['required']}) "
                                f"is greater than the available {cost_estimation['available']}")


def create(user_id: str, email: str, cfg: AnyDict, token: Optional[str] = None, info_only: bool = False) -> Union[AnyDict, Error]:
    try:
        if 'input_config' not in cfg and 'input_configs' not in cfg:
            raise api.ApiError(400, "Either 'input_config' or 'input_configs' must be given")

        token = token or Auth.instance().token

        if not info_only:
            _raise_for_invalid_punits(user_id=user_id, email=email, cfg=cfg, token=token)

        xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
        user_namespaces.create_if_not_exists(user_namespace=xcube_hub_namespace)
        callback_uri = os.getenv('XCUBE_HUB_CALLBACK_URL', False)

        if callback_uri is False:
            raise api.ApiError(400, "XCUBE_HUB_CALLBACK_URL must be given")

        job_id = f"{user_id}-{str(uuid.uuid4())[:18]}"

        cfg['callback_config'] = dict(api_uri=callback_uri + f'/cubegens/{job_id}/callbacks',
                                      access_token=token)

        if not cfg['output_config'].get('data_id'):
            cfg['output_config']['data_id'] = job_id + '.zarr'

        job = create_cubegen_object(job_id, cfg=cfg, info_only=info_only)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=xcube_hub_namespace)

        kvdb = KeyValueDatabase.instance()
        kvdb.set(user_id + '__' + job_id + '__cfg', cfg)
        kvdb.set(user_id + '__' + job_id, {'progress': []})

        return {'cubegen_id': job_id, 'status': api_response.status.to_dict()}
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, message=str(e))


# noinspection PyShadowingBuiltins
def list(user_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.list_namespaced_job(namespace=xcube_hub_namespace)

        res = []
        for job in api_response.items:
            if user_id in job.metadata.name:
                job = get(user_id=user_id, cubegen_id=job.metadata.name)

                res.append(job)

        return api.ApiResponse.success(res)
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def logs(job_id: str) -> Sequence:
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    api_pod_instance = client.CoreV1Api()

    lgs = []
    try:
        pods = api_pod_instance.list_namespaced_pod(namespace=xcube_hub_namespace, label_selector=f"job-name={job_id}")

        for pod in pods.items:
            name = pod.metadata.name

            lg = api_pod_instance.read_namespaced_pod_log(namespace=xcube_hub_namespace, name=name)

            lgs.append(lg)
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        pprint(str(e))

    return lgs


def status(job_id: str) -> AnyDict:
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    api_instance = client.BatchV1Api()
    try:
        api_response = api_instance.read_namespaced_job_status(namespace=xcube_hub_namespace, name=job_id)
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        print(str(e))
        return {}

    return api_response.status.to_dict()


def delete_one(cubegen_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("K8S_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.delete_namespaced_job(
            name=cubegen_id,
            namespace=xcube_hub_namespace,
            body=client.V1DeleteOptions(propagation_policy='Background', grace_period_seconds=5))
        return api_response.status
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def delete_all(user_id: str) -> Union[AnyDict, Error]:
    try:
        jobs = list(user_id=user_id)
        for job in jobs['result']:
            delete_one(job['cubegen_id'])
        return api.ApiResponse.success("SUCCESS")
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def info(user_id: str, email: str, body: JsonObject, token: Optional[str] = None) -> JsonObject:
    data_pools_cfg_file = os.getenv("XCUBE_GEN_DATA_POOLS_PATH", None)
    if data_pools_cfg_file is None:
        raise api.ApiError(400, "XCUBE_GEN_DATA_POOLS_PATH is not configured.")

    try:
        with open(data_pools_cfg_file, 'r') as f:
            data_pools = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise api.ApiError(400, f"Datapools file {data_pools_cfg_file} not found. " + str(e))

    job = create(user_id=user_id, email=email, cfg=body, info_only=True, token=token)
    apps_v1_api = client.BatchV1Api()
    poller.poll_job_status(apps_v1_api.read_namespaced_job_status, namespace="xcube-gen-stage",
                           name=job['cubegen_id'])
    state = get(user_id=user_id, cubegen_id=job['cubegen_id'])
    res = state['output'][0]
    res = res.replace("Awaiting generator configuration JSON from TTY...", "")
    res = res.replace("Cube generator configuration loaded from TTY.", "")
    processing_request = json.loads(res)
    input_config = get_json_request_value(body, 'input_config',
                                          value_type=dict,
                                          item_type=dict,
                                          default_value={})

    store_id = get_json_request_value(input_config, 'store_id',
                                      value_type=str,
                                      default_value="")

    store_id = store_id.replace('@', '')
    try:
        data_store = data_pools[store_id]

    except KeyError:
        raise api.ApiError(400, f'unsupported "input_config/datastore_id" entry: "{store_id}"')

    available = punits.get_punits(user_id=email)

    if 'count' not in available:
        raise api.ApiError(400, "Error. Cannot handle punit data. Entry 'count' is missing.")

    cost_est = costs.get_size_and_cost(processing_request=processing_request, datastore=data_store)
    required = cost_est['punits']['total_count']

    limit = os.getenv("XCUBE_HUB_PROCESS_LIMIT", 1000)

    return dict(
        dataset_descriptor=cost_est['dataset_descriptor'],
        size_estimation=cost_est['size_estimation'],
        cost_estimation=dict(required=required, available=available['count'], limit=int(limit))
    )
