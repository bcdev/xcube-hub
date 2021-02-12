import connexion
from xcube_hub.models.api_job_response import ApiJobResponse  # noqa: E501
from xcube_hub.models.api_jobs_response import ApiJobsResponse  # noqa: E501
from xcube_hub.models.api_service_information_response import ApiServiceInformationResponse  # noqa: E501
from xcube_hub.models.cost_config import CostConfig  # noqa: E501
from xcube_hub.models.job_config import JobConfig  # noqa: E501


def create_job(body):  # noqa: E501
    """Create a job

    Create a job  # noqa: E501

    :param body: Job configuration
    :type body: dict | bytes

    :rtype: ApiJobResponse
    """
    if connexion.request.is_json:
        body = JobConfig.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_job(job_id):  # noqa: E501
    """Delete a job

    Delete a job  # noqa: E501

    :param job_id: Job ID
    :type job_id: str

    :rtype: None
    """
    return 'do some magic!'


def delete_jobs():  # noqa: E501
    """Delete all jobs

    Delete all jobs  # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def get_costs(body):  # noqa: E501
    """Receive cost information for runnning a job

    Receive cost information of using a service  # noqa: E501

    :param body: Cost configuration
    :type body: dict | bytes

    :rtype: ApiServiceInformationResponse
    """
    if connexion.request.is_json:
        body = CostConfig.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_job(job_id):  # noqa: E501
    """List specific job

    List specific job  # noqa: E501

    :param job_id: Job ID
    :type job_id: str

    :rtype: ApiJobResponse
    """
    return 'do some magic!'


def get_jobs():  # noqa: E501
    """List jobs

    List user jobs  # noqa: E501


    :rtype: ApiJobsResponse
    """
    return 'do some magic!'
