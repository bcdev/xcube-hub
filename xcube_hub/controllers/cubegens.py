import connexion
from xcube_hub.models.api_service_information_response import ApiServiceInformationResponse
from xcube_hub.models.cost_config import CostConfig
from xcube_hub.models.cubegen_config import CubegenConfig


def create_cubegen(body: CubegenConfig):
    """Create a cubegen

    Create a cubegen

    :param body: CubeGen configuration
    :type body: dict | bytes

    :rtype: ApiCubeGenResponse
    """
    if connexion.request.is_json:
        body = CubegenConfig.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_cubegen(cubegen_id):  # noqa: E501
    """Delete a cubegen

    Delete a cubegen  # noqa: E501

    :param cubegen_id: CubeGen ID
    :type cubegen_id: str

    :rtype: None
    """
    return 'do some magic!'


def delete_cubegens():  # noqa: E501
    """Delete all cubegens

    Delete all cubegens  # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


def get_costs(body):  # noqa: E501
    """Receive cost information for runnning a cubegen

    Receive cost information of using a service  # noqa: E501

    :param body: Cost configuration
    :type body: dict | bytes

    :rtype: ApiServiceInformationResponse
    """
    if connexion.request.is_json:
        body = CostConfig.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_cubegen(cubegen_id):  # noqa: E501
    """List specific cubegen

    List specific cubegen  # noqa: E501

    :param cubegen_id: CubeGen ID
    :type cubegen_id: str

    :rtype: ApiCubeGenResponse
    """
    return 'do some magic!'


def get_cubegens():  # noqa: E501
    """List cubegens

    List user cubegens  # noqa: E501


    :rtype: ApiCubeGensResponse
    """
    return 'do some magic!'
