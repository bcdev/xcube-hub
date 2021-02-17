from xcube_hub import api
from xcube_hub.controllers import costs, authorization
from xcube_hub.core import cubegens
from xcube_hub.typedefs import JsonObject


def create_cubegen(body: JsonObject):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: dict | bytes

    :rtype: ApiCubeGenResponse
    """

    try:
        user_id = authorization.get_user_id()

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


def delete_cubegens():
    """Delete all cubegens

    Delete all cubegens


    :rtype: None
    """

    try:
        user_id = authorization.get_user_id()
        cubegens.delete_all(user_id=user_id)
        return api.ApiResponse.success("Success")
    except api.ApiError as e:
        return e.response


def get_costs(body):
    """Receive cost information for runnning a cubegen

    Receive cost information of using a service

    :param body: Cost configuration
    :type body: dict | bytes

    :rtype: ApiServiceInformationResponse
    """

    try:
        result = costs.get_size_and_cost(processing_request=body)
        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response


def get_cubegen(cubegen_id):
    """List specific cubegen

    List specific cubegen

    :param cubegen_id: CubeGen ID
    :type cubegen_id: str

    :rtype: ApiCubeGenResponse
    """

    try:
        user_id = authorization.get_user_id()
        res = cubegens.get(user_id=user_id, cubegen_id=cubegen_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def get_cubegens():
    """List cubegens

    List user cubegens


    :rtype: ApiCubeGensResponse
    """

    try:
        user_id = authorization.get_user_id()
        res = cubegens.list(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response

