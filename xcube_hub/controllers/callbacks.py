import connexion
from xcube_hub.models.api_callback_response import ApiCallbackResponse  # noqa: E501
from xcube_hub.models.callback import Callback  # noqa: E501


def delete_callbacks_by_cubegen_id(cubegen_id):  # noqa: E501
    """Clear callbacks for a cubegen

    Clear callbacks for a cubegen # noqa: E501

    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: None
    """
    return 'do some magic!'


def get_callbacks_by_cubegen_id(cubegen_id):  # noqa: E501
    """Get list of callbacks for a cubegen

    Get list of callbacks for a cubegen # noqa: E501

    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: List[ApiCallbacksResponse]
    """
    return 'do some magic!'


def put_callback_by_cubegen_id(body, cubegen_id):  # noqa: E501
    """Add a callback for a cubegen

    Add a callbacks for a cubegen # noqa: E501

    :param body: Callbacks
    :type body: list | bytes
    :param cubegen_id: Job ID
    :type cubegen_id: str

    :rtype: ApiCallbackResponse
    """
    if connexion.request.is_json:
        body = [Callback.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
