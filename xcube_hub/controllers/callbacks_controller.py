import connexion
from xcube_hub.models.api_callback_response import ApiCallbackResponse  # noqa: E501
from xcube_hub.models.callback import Callback  # noqa: E501


def delete_callbacks_by_job_id(job_id):  # noqa: E501
    """Clear callbacks for a job

    Clear callbacks for a job # noqa: E501

    :param job_id: Job ID
    :type job_id: str

    :rtype: None
    """
    return 'do some magic!'


def get_callbacks_by_job_id(job_id):  # noqa: E501
    """Get list of callbacks for a job

    Get list of callbacks for a job # noqa: E501

    :param job_id: Job ID
    :type job_id: str

    :rtype: List[ApiCallbacksResponse]
    """
    return 'do some magic!'


def put_callback_by_job_id(body, job_id):  # noqa: E501
    """Add a callback for a job

    Add a callbacks for a job # noqa: E501

    :param body: Callbacks
    :type body: list | bytes
    :param job_id: Job ID
    :type job_id: str

    :rtype: ApiCallbackResponse
    """
    if connexion.request.is_json:
        body = [Callback.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'
