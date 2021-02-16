import connexion

from xcube_hub import api
from xcube_hub.k8s_controllers import callbacks
from xcube_hub.models.callback import Callback


def delete_callbacks_by_cubegen_id(cubegen_id):
    """Clear callbacks for a cubegen

    Clear callbacks for a cubegen

    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: None
    """
    try:
        result = callbacks.delete_callback(user_id="dfvdfsv", cubegen_id=cubegen_id)
        return api.ApiResponse.success(result)
    except TimeoutError as r:
        raise api.ApiError(401, r.strerror)


def get_callbacks_by_cubegen_id(cubegen_id):
    """Get list of callbacks for a cubegen

    Get list of callbacks for a cubegen

    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: List[ApiCallbacksResponse]
    """

    try:
        result = callbacks.get_callback(user_id="dfv", cubegen_id=cubegen_id)
        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response


def put_callback_by_cubegen_id(body, cubegen_id):
    """Add a callback for a cubegen

    Add a callbacks for a cubegen

    :param body: Callbacks
    :type body: list | bytes
    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: ApiCallbackResponse
    """
    try:
        if not connexion.request.is_json:
            raise api.ApiError(400, "Not a json request.")

        callbks = [Callback.from_dict(d) for d in body]

        result = []
        for callback in callbks:
            result.append(callbacks.put_callback(user_id="dfsv", cubegen_id=cubegen_id, value=callback.to_dict()))

        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response
