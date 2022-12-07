import os

from xcube_hub import api
from xcube_hub.core import cate


def _maybe_raise_for_service_silent():
    cate_silent = os.getenv("CATE_SILENT", default=None)

    if cate_silent == '1':
        raise api.ApiError(422, "Cate resources are switched off on this service")


def put_user_webapi(user_id: str):
    try:
        _maybe_raise_for_service_silent()
        res = cate.launch_cate(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def get_user_webapi(user_id: str):
    try:
        _maybe_raise_for_service_silent()
        res = cate.get_status(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def delete_user_webapi(user_id: str):
    try:
        _maybe_raise_for_service_silent()
        res = cate.delete_cate(user_id=user_id, prune=True, check_namespace=False)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response
