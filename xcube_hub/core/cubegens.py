import json
import os
import uuid
from pprint import pprint
from typing import Union, Sequence, Optional, Tuple, Dict

from kubernetes import client
from kubernetes.client import ApiException, ApiValueError
from urllib3.exceptions import MaxRetryError
from werkzeug.datastructures import FileStorage

from xcube_hub import api, poller, util
from xcube_hub.api import get_json_request_value
from xcube_hub.cfg import Cfg
from xcube_hub.core import callbacks, costs, punits
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.models.cubegen_config import CubegenConfig
from xcube_hub.typedefs import AnyDict, Error, JsonObject
from xcube_hub.util import maybe_raise_for_env


def get(user_id: str, cubegen_id: str) -> Tuple[JsonObject, int]:
    try:
        outputs = logs(job_id=cubegen_id)
        stat = status(job_id=cubegen_id)

        if not stat:
            raise api.ApiError(404, message=f"Cubegen {cubegen_id} not found")

        progress = callbacks.get_callback(user_id=user_id, cubegen_id=cubegen_id)

        xcube_hub_result_root_dir = util.maybe_raise_for_env("XCUBE_HUB_RESULT_ROOT_DIR")
        res = cubegens_result(job_id=cubegen_id, root=xcube_hub_result_root_dir)

        if 'output' not in res:
            res['output'] = outputs
        else:
            res['output'] += outputs

        status_code = res['status_code'] if 'status_code' in res else 200

        res = {'job_id': cubegen_id,
               'job_status': stat,
               'job_result': res,
               'output': outputs,
               'progress': progress}

        return res, status_code
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def create_cubegen_object(cubegen_id: str, cfg: AnyDict, info_only: bool = False) -> client.V1Job:
    # Configure Pod template container
    sh_client_id = os.environ.get("SH_CLIENT_ID")
    sh_client_secret = os.environ.get("SH_CLIENT_SECRET")
    sh_instance_id = os.environ.get("SH_INSTANCE_ID")

    xcube_repo = util.maybe_raise_for_env("XCUBE_REPO")
    xcube_tag = util.maybe_raise_for_env("XCUBE_TAG")
    xcube_hash = os.getenv("XCUBE_HASH", default=None)

    gen_container_pull_policy = os.environ.get("XCUBE_GEN_DOCKER_PULL_POLICY")
    cdsapi_url = os.getenv("CDSAPI_URL")
    cdsapi_key = os.getenv("CDSAPI_KEY")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    xcube_hub_cfg_dir = util.maybe_raise_for_env("XCUBE_HUB_CFG_DIR")
    xcube_hub_cfg_datapools = util.maybe_raise_for_env("XCUBE_HUB_CFG_DATAPOOLS")
    stores_file = os.path.join(xcube_hub_cfg_dir, xcube_hub_cfg_datapools)

    if xcube_hash is not None and xcube_hash != "null":
        gen_image = xcube_repo + '@' + xcube_hash
    else:
        gen_image = xcube_repo + ':' + xcube_tag

    if not sh_client_secret or not sh_client_id or not sh_instance_id:
        raise api.ApiError(400, "SentinelHub credentials not set.")

    if not cdsapi_url or not cdsapi_key:
        raise api.ApiError(400, "CDS credentials not set.")

    if not cfg:
        raise api.ApiError(400, "create_gen_cubegen_object needs a config dict.")

    info_flag = " -i " if info_only else ""

    xcube_hub_code_root_dir = util.maybe_raise_for_env('XCUBE_HUB_CODE_ROOT_DIR')
    xcube_hub_result_root_dir = util.maybe_raise_for_env("XCUBE_HUB_RESULT_ROOT_DIR")

    if not os.path.isdir(xcube_hub_code_root_dir):
        os.mkdir(xcube_hub_code_root_dir)

    if not os.path.isdir(xcube_hub_result_root_dir):
        os.mkdir(xcube_hub_result_root_dir)

    cfg_file = os.path.join(xcube_hub_code_root_dir, cubegen_id + '.yaml')
    res_file = os.path.join(xcube_hub_result_root_dir, cubegen_id + '.json')

    with open(cfg_file, 'w') as f:
        json.dump(cfg, f)

    cmd = f"source activate xcube && xcube --traceback gen2 -o {res_file} -vv {info_flag} " \
          f"--stores {stores_file} {cfg_file}"
    # cmd = cmd + " && curl -X POST localhost:3500/v1.0/shutdown" if xcube_use_dapr else None

    cmd = ["/bin/bash", "-c", cmd]

    sh_envs = [
        client.V1EnvVar(name="SH_CLIENT_ID", value=sh_client_id),
        client.V1EnvVar(name="SH_CLIENT_SECRET", value=sh_client_secret),
        client.V1EnvVar(name="SH_INSTANCE_ID", value=sh_instance_id),
        client.V1EnvVar(name="CDSAPI_URL", value=cdsapi_url),
        client.V1EnvVar(name="CDSAPI_KEY", value=cdsapi_key),
        client.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=aws_access_key_id),
        client.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=aws_secret_access_key)
    ]

    volume_mounts = [
        {
            'name': 'xcube-hub-stores',
            'mountPath': '/etc/xcube-hub',
            'readOnly': True
        },
        {
            'name': 'workspace-pvc',
            'mountPath': '/data',
        },
    ]

    volumes = [
        {
            'name': 'xcube-hub-stores',
            'configMap': {
                'name': 'xcube-hub-stores'
            }
        },
        {
            'name': 'workspace-pvc',
            'persistentVolumeClaim': {
                'claimName': 'workspace-pvc',
            }
        },
    ]

    # annotations = {"dapr.io/app-id": cubegen_id, "dapr.io/enabled": "true",
    #                "dapr.io/log-as-json": "true"} if xcube_use_dapr else None

    container = client.V1Container(
        name="xcube-gen",
        image=gen_image,
        command=cmd,
        volume_mounts=volume_mounts,
        image_pull_policy=gen_container_pull_policy,
        env=sh_envs)
    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={"app": "xcube-gen"},
            # annotations=annotations
        ),
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

    infos, status_code = info(user_id=user_id, email=email, body=cfg, token=token)
    cost_estimation = infos['result']['cost_estimation']

    if cost_estimation['required'] > int(limit):
        raise api.ApiError(413,
                           f"Number of required punits ({cost_estimation['required']}) is "
                           f"greater than the absolute limit of {limit}.")

    if cost_estimation['required'] > cost_estimation['available']:
        raise api.ApiError(413, f"Number of required punits ({cost_estimation['required']}) "
                                f"is greater than the available ({cost_estimation['available']}).")


def create(user_id: str, email: str, cfg: AnyDict, token: Optional[str] = None, info_only: bool = False) -> \
        Tuple[JsonObject, int]:
    try:
        if 'input_config' not in cfg and 'input_configs' not in cfg:
            raise api.ApiError(400, "Either 'input_config' or 'input_configs' must be given")

        if not info_only:
            _raise_for_invalid_punits(user_id=user_id, token=token, email=email, cfg=cfg)

        xcube_hub_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
        # Not used as the namespace cate has to be created prior to launching cubegens instances
        # user_namespaces.create_if_not_exists(user_namespace=xcube_hub_namespace)
        callback_uri = os.getenv('XCUBE_HUB_CALLBACK_URL', False)

        if callback_uri is False:
            raise api.ApiError(400, "XCUBE_HUB_CALLBACK_URL must be given")

        job_id = f"{user_id}-{str(uuid.uuid4())[:18]}"

        cfg['callback_config'] = dict(api_uri=callback_uri + f'/cubegens/{job_id}/callbacks',
                                      access_token=token)

        if 'data_id' not in cfg['output_config']:
            cfg['output_config']['data_id'] = job_id + '.zarr'

        job = create_cubegen_object(job_id, cfg=cfg, info_only=info_only)
        api_instance = client.BatchV1Api()
        api_response = api_instance.create_namespaced_job(body=job, namespace=xcube_hub_namespace)

        kvdb = KeyValueDatabase.instance()
        kvdb.set(user_id + '__' + job_id + '__cfg', cfg)
        kvdb.set(user_id + '__' + job_id, {'progress': []})

        job_result = dict(output=[], status_code=200, status='ok')

        return {'job_id': job_id, 'job_status': api_response.status.to_dict(), 'job_result': job_result}, 200
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, message=str(e))
    except Exception as e:
        raise api.ApiError(400, message=str(e))


# noinspection PyShadowingBuiltins
def list(user_id: str):
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.list_namespaced_job(namespace=xcube_hub_namespace)

        res = []
        for job in api_response.items:
            if user_id in job.metadata.name:
                job, status_code = get(user_id=user_id, cubegen_id=job.metadata.name)

                res.append(job)

        return res, 200
    except (ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def cubegens_result(job_id: str, root: str) -> Dict:
    try:
        if not os.path.isdir(root):
            os.mkdir(root)

        fn = os.path.join(root, job_id + '.json')

        if os.path.isfile(fn):
            with open(fn, 'r') as f:
                return json.load(f)
        else:
            return dict(status_code=404, status='warning')
    except Exception as e:
        raise api.ApiError(400, str(e))


def logs(job_id: str, raises: bool = False) -> Sequence:
    xcube_hub_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
    api_pod_instance = client.CoreV1Api()

    lgs = []
    try:
        pods = api_pod_instance.list_namespaced_pod(namespace=xcube_hub_namespace, label_selector=f"job-name={job_id}")

        for pod in pods.items:
            name = pod.metadata.name

            lg = api_pod_instance.read_namespaced_pod_log(namespace=xcube_hub_namespace, name=name)
            lg = lg.splitlines()
            lgs += lg
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        if raises:
            raise api.ApiError(400, str(e))
        pprint(str(e))

    return lgs


def status(job_id: str) -> AnyDict:
    xcube_hub_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
    api_instance = client.BatchV1Api()
    try:
        api_response = api_instance.read_namespaced_job_status(namespace=xcube_hub_namespace, name=job_id)
    except (client.ApiValueError, client.ApiException, MaxRetryError) as e:
        print(str(e))
        return {}

    return api_response.status.to_dict()


def delete_one(cubegen_id: str) -> Union[AnyDict, Error]:
    api_instance = client.BatchV1Api()
    xcube_hub_namespace = os.getenv("WORKSPACE_NAMESPACE", "xcube-gen-dev")
    try:
        api_response = api_instance.delete_namespaced_job(
            name=cubegen_id,
            namespace=xcube_hub_namespace,
            body=client.V1DeleteOptions(propagation_policy='Background', grace_period_seconds=5))
        return api_response.status
    except (ApiValueError, ApiException, MaxRetryError) as e:
        raise api.ApiError(400, str(e))


def delete_all(user_id: str):
    jobs, status_code = list(user_id=user_id)

    for job in jobs:
        delete_one(job['cubegen_id'])


def info(user_id: str, email: str, body: JsonObject, token: Optional[str] = None) -> Tuple[JsonObject, int]:
    xcube_hub_result_root_dir = util.maybe_raise_for_env("XCUBE_HUB_RESULT_ROOT_DIR")

    job, status_code = create(user_id=user_id, email=email, cfg=body, info_only=True, token=token)

    apps_v1_api = client.BatchV1Api()
    xcube_hub_namespace = maybe_raise_for_env("WORKSPACE_NAMESPACE", "xc-gen")
    poller.poll_job_status(apps_v1_api.read_namespaced_job_status, namespace=xcube_hub_namespace,
                           name=job['job_id'])

    state, status_code = get(user_id=user_id, cubegen_id=job['job_id'])
    job_result = cubegens_result(job_id=job['job_id'], root=xcube_hub_result_root_dir)

    output = state['output']

    processing_request = job_result['result']

    if 'input_configs' in body:
        input_config = body['input_configs'][0]
    elif 'input_config' in body:
        input_config = body['input_config']
    else:
        raise api.ApiError(400, "Error. Invalid input configuration.")

    store_id = get_json_request_value(input_config, 'store_id',
                                      value_type=str,
                                      default_value="")

    store_id = store_id.replace('@', '')
    data_store = Cfg.get_datastore(store_id)

    available = punits.get_punits(user_id=email)

    if 'count' not in available:
        raise api.ApiError(400, "Error. Cannot handle punit data. Entry 'count' is missing.")

    cost_est = costs.get_size_and_cost(processing_request=processing_request, datastore=data_store)
    required = cost_est['punits']['total_count']

    limit = os.getenv("XCUBE_HUB_PROCESS_LIMIT", 1000)
    job_result['result']['cost_estimation'] = dict(required=required, available=available['count'], limit=int(limit))
    job_result['result']['size_estimation'] = cost_est['size_estimation']
    job_result['output'] = output
    job_result['result']['status'] = job_result['status']
    status_code = job_result['status_code']

    return job_result, status_code


def process_user_code(cfg: CubegenConfig, user_code: Optional[FileStorage] = None):
    if user_code is not None:
        code_dir = uuid.uuid4().hex
        code_root_dir = util.maybe_raise_for_env('XCUBE_HUB_CODE_ROOT_DIR')
        filename = user_code.filename

        code_dir = os.path.join(code_root_dir, code_dir)

        if not os.path.isdir(code_dir):
            os.mkdir(code_dir)

        code_path = os.path.join(code_dir, filename)

        user_code.save(code_path)

        cfg.code_config.file_set.path = code_path

    return cfg
