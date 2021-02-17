import connexion

from xcube_hub import api
from xcube_hub.controllers import authorization
from xcube_hub.core import callbacks
from xcube_hub.models.callback import Callback


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
        user_id = authorization.get_user_id()

        result = []
        for callback in callbks:
            result.append(callbacks.put_callback(user_id=user_id, cubegen_id=cubegen_id, value=callback.to_dict()))

        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response
