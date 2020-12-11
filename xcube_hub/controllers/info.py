import datetime
import os

from xcube_hub.api import SERVER_DESCRIPTION
from xcube_hub.api import SERVER_NAME
from xcube_hub.api import SERVER_START_TIME
from xcube_hub.typedefs import JsonObject
from xcube_hub.version import version


def service_info() -> JsonObject:
    return dict(name=SERVER_NAME,
                description=SERVER_DESCRIPTION,
                version=version,
                serverStartTime=SERVER_START_TIME,
                serverCurrentTime=datetime.datetime.now().isoformat(),
                serverPID=os.getpid(),
                chartVersion=os.getenv("XCUBE_GEN_CHART_VERSION"),
                mockServices=os.getenv("XCUBE_GEN_MOCK_SERVICES"),
                runLocal=os.getenv("XCUBE_GEN_API_RUN_LOCAL"))
