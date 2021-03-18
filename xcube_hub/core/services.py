import os

from xcube_hub import api
from xcube_hub.typedefs import JsonObject
from xcube_hub.util import maybe_raise_for_env


_SERVICES = ["xcube-gen", "cate"]


def get_service(service_id: str):
    if service_id not in _SERVICES:
        raise api.ApiError(404, "Service not found")

    status = maybe_raise_for_env("XCUBE_HUB_GEN_STATUS")
    message = maybe_raise_for_env("XCUBE_HUB_GEN_MESSAGE")

    return dict(name=service_id, status=status, message=message)


def patch_service(service_id: str, body: JsonObject):
    if service_id not in _SERVICES:
        raise api.ApiError(404, "Service not found")

    os.environ["XCUBE_HUB_GEN_STATUS"] = body['status']
    os.environ["XCUBE_HUB_GEN_MESSAGE"] = body['message']

    return body
