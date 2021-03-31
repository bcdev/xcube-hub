from typing import Dict

from xcube_hub import api
from xcube_hub.core import cubegens
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
        email = token_info['email']

        cubegen = cubegens.create(user_id=user_id, email=email, cfg=body)
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
        email = token_info['email']

        result = cubegens.info(user_id=user_id, email=email, body=body)

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
