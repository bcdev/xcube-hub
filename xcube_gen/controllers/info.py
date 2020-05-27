import datetime
import os

from xcube_gen.api import SERVER_DESCRIPTION
from xcube_gen.api import SERVER_NAME
from xcube_gen.api import SERVER_START_TIME
from xcube_gen.xg_types import JsonObject
from xcube_gen.version import version


def service_info() -> JsonObject:
    return dict(name=SERVER_NAME,
                description=SERVER_DESCRIPTION,
                version=version,
                serverStartTime=SERVER_START_TIME,
                serverCurrentTime=datetime.datetime.now().isoformat(),
                serverPID=os.getpid(),
                chartVersion=os.getenv("XCUBE_GEN_CHART_VERSION"),
                mockServices=os.getenv("XCUBE_GEN_MOCK_SERVICES"),
                runLocal=os.getenv("RUN_LOCAL"))
