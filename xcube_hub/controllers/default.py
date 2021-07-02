import datetime
import os

from xcube_hub import api
from xcube_hub.api import SERVER_NAME, SERVER_DESCRIPTION, SERVER_START_TIME
from xcube_hub.version import version


def get_service_info():
    """get service info

    Get service info


    :rtype: ApiServiceInformationResponse
    """
    res = dict(name=SERVER_NAME,
               description=SERVER_DESCRIPTION,
               version=version,
               xcubeDockerTag=os.getenv("XCUBE_TAG"),
               serverStartTime=SERVER_START_TIME,
               serverCurrentTime=datetime.datetime.now().isoformat(),
               serverPID=os.getpid(),
               chartVersion=os.getenv("XCUBE_HUB_CHART_VERSION"),
               mockServices=os.getenv("XCUBE_HUB_MOCK_SERVICES"),
               runLocal=os.getenv("XCUBE_HUB_RUN_LOCAL"))
    return api.ApiResponse.success(result=res)
