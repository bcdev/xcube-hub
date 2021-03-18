from xcube_hub import api
from xcube_hub.core import services
from xcube_hub.typedefs import JsonObject


def get_service(service_id: str):
    try:
        svcs = services.get_service(service_id=service_id)
        return api.ApiResponse.success(svcs)

    except api.ApiError as e:
        return e.response


def patch_service(service_id: str, body: JsonObject, token_info: JsonObject):
    try:
        svcs = services.patch_service(service_id=service_id, body=body)
        return api.ApiResponse.success(svcs)

    except api.ApiError as e:
        return e.response
