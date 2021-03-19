from xcube_hub import api
from xcube_hub.util import maybe_raise_for_env


_SERVICES = ["xcube_gen", "cate"]


def get_services():
    return api.ApiResponse.success(_SERVICES)


def get_service(service_id: str):
    if service_id not in _SERVICES:
        raise api.ApiError(404, "Service not found")

    service = service_id.upper()

    status = maybe_raise_for_env(f"XCUBE_HUB_{service}_STATUS")
    message = maybe_raise_for_env(f"XCUBE_HUB_{service}_MESSAGE")

    return dict(name=service_id, status=status, message=message)

