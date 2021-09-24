import json
from typing import Dict, Tuple

from werkzeug.datastructures import FileStorage

from xcube_hub import api
from xcube_hub.core import cubegens
from xcube_hub.core.cubegens import process_user_code
from xcube_hub.models.cubegen_config import CubegenConfig
from xcube_hub.typedefs import AnyDict, JsonObject


def _maybe_raise_for_process_not_allowed(body: JsonObject, token_info: Dict):
    if 'code_config' in body:
        if 'scopes' in token_info and 'process:cubegens' not in token_info['scopes']:
            raise api.ApiError(403, "You don't have access to using byoa code.")


def create_cubegen(body: JsonObject, token_info: Dict):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: JsonObject
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGenResponse
    """
    try:
        user_id = token_info['user_id']
        email = token_info['email']
        token = token_info['token']

        _maybe_raise_for_process_not_allowed(body, token_info)
        cubegen, status_code = cubegens.create(user_id=user_id, email=email, token=token, cfg=body)
        return api.ApiResponse.success(cubegen, status_code=status_code)
    except api.ApiError as e:
        return e.response


def create_cubegen_code(body: FileStorage, user_code: FileStorage, token_info: Dict):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: FileStorage
    :param user_code: Token claims
    :type user_code: FileStorage
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCubeGenResponse
    """
    try:
        body_dict = json.load(body.stream)

        body = CubegenConfig.from_dict(body_dict)
        body = process_user_code(cfg=body, user_code=user_code)
        body = body.to_dict()

        user_id = token_info['user_id']
        email = token_info['email']
        token = token_info['token']

        cubegen, status_code = cubegens.create(user_id=user_id, email=email, token=token, cfg=body)
        return api.ApiResponse.success(cubegen, status_code=status_code)
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
    """Receive cost information for running a cubegen

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

        result, status_code = cubegens.info(user_id=user_id, email=email, token=token, body=body)

        return api.ApiResponse.success(result=result, status_code=status_code)
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
        res, status_code = cubegens.get(user_id=user_id, cubegen_id=cubegen_id)
        return api.ApiResponse.success(res, status_code=status_code)
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
