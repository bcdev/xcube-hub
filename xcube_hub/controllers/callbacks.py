from xcube_hub import api
from xcube_hub.core import callbacks
from xcube_hub.models.callback import Callback


def put_callback_by_cubegen_id(body, cubegen_id, token_info):
    """Add a callback for a cubegen

    Add a callbacks for a cubegen

    :param body: Callbacks
    :type body: list | bytes
    :param cubegen_id: Job ID
    :type cubegen_id: str
    :param token_info: Token claims
    :type token_info: Dict

    :rtype: ApiCallbackResponse
    """
    try:
        callback = Callback.from_dict(body)
        result = callbacks.put_callback(user_id=token_info['user_id'], email=token_info['email'], cubegen_id=cubegen_id,
                                        value=callback.to_dict())

        return api.ApiResponse.success(result=result)
    except api.ApiError as e:
        return e.response
