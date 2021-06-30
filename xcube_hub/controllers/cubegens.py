import json
from typing import Dict, Tuple

from flask import request
from werkzeug.datastructures import FileStorage

from xcube_hub import api
from xcube_hub.core import cubegens
from xcube_hub.core.cubegens import process_user_code
from xcube_hub.models.cubegen_config import CubegenConfig
from xcube_hub.typedefs import AnyDict, JsonObject


def create_cubegen(body: FileStorage, token_info: Dict):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: FileStorage
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGenResponse
    """
    files = request.files
    user_code = files.get('user_code')

    body_dict = json.load(body.stream)
    body = CubegenConfig.from_dict(body_dict)

    try:
        user_id = token_info['user_id']
        email = token_info['email']
        token = token_info['token']

        body = process_user_code(cfg=body, user_code=user_code)

        cubegen = cubegens.create(user_id=user_id, email=email, token=token, cfg=body.to_dict())
        return api.ApiResponse.success(cubegen)
    except api.ApiError as e:
        return e.response


def delete_cubegen(cubegen_id) -> Tuple[AnyDict, int]:
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


def delete_cubegens(token_info: JsonObject) -> Tuple:
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
        token = token_info['token']

        result = cubegens.info(user_id=user_id, email=email, token=token, body=body)

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
