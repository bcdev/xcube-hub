import json
from typing import Dict

import yaml
from kubernetes import client

from xcube_hub import api, poller
from xcube_hub.api import get_json_request_value
from xcube_hub.core import cubegens, costs
from xcube_hub.typedefs import JsonObject


def create_cubegen(body: JsonObject, token_info: Dict):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: dict | bytes
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGenResponse
    """

    try:
        user_id = token_info['user_id']

        cubegen = cubegens.create(user_id=user_id, cfg=body)
        return api.ApiResponse.success(cubegen)
    except api.ApiError as e:
        return e.response


def delete_cubegen(cubegen_id):
    """Delete a cubegen

    Delete a cubegen

    :param cubegen_id: CubeGen ID
    :type cubegen_id: str

    :rtype: None
    """

    try:
        status = cubegens.delete_one(cubegen_id=cubegen_id)
        return api.ApiResponse.success(status)
    except api.ApiError as e:
        return e.response


def delete_cubegens(token_info):
    """Delete all cubegens

    Delete all cubegens


    :rtype: None
    """

    try:
        user_id = token_info['user_id']
        cubegens.delete_all(user_id=user_id)
        return api.ApiResponse.success("Success")
    except api.ApiError as e:
        return e.response


def get_cubegen_info(body, token_info: Dict):
    """Receive cost information for runnning a cubegen

    Receive cost information of using a service

    :param token_info:
    :param body: Cost configuration
    :type body: dict | bytes

    :rtype: ApiServiceInformationResponse
    """

    try:
        user_id = token_info['user_id']
        data_pools = yaml.safe_load(open('xcube_hub/resources/data-pools.yaml', 'r'))

        job = cubegens.create(user_id=user_id, cfg=body, info_only=True)
        apps_v1_api = client.BatchV1Api()
        poller.poll_job_status(apps_v1_api.read_namespaced_job_status, namespace="xcube-gen-stage",
                               name=job['cubegen_id'])
        status = cubegens.get(user_id=user_id, cubegen_id=job['cubegen_id'])
        res = status['output'][0]
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

        result = costs.get_size_and_cost(processing_request=processing_request, datastore=data_store)
        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response


def get_cubegen(cubegen_id, token_info):
    """List specific cubegen

    List specific cubegen

    :param cubegen_id: CubeGen ID
    :type cubegen_id: str
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGenResponse
    """

    try:
        user_id = token_info['user_id']
        res = cubegens.get(user_id=user_id, cubegen_id=cubegen_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def get_cubegens(token_info):
    """List cubegens

    List user cubegens

    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGensResponse
    """

    try:
        user_id = token_info['user_id']
        res = cubegens.list(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response
