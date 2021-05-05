from xcube_hub import api
from xcube_hub.core import cate


def put_user_webapi(user_id: str):
    try:
        res = cate.launch_cate(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def get_user_webapi(user_id: str):
    try:
        res = cate.get_status(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def delete_user_webapi(user_id: str):
    try:
        res = cate.delete_cate(user_id=user_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response
