from xcube_hub import api
from xcube_hub.core import xcube
from xcube_hub.typedefs import JsonObject


def create_xcube(body: JsonObject):
    try:
        user_id = body['user_id']
        cfg = body['cfg']
        res = xcube.create(user_id=user_id, cfg=cfg)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def delete_xcube(user_id: str):
    try:
        xcube.delete(user_id=user_id)
        return api.ApiResponse.success('SUCCESS')
    except api.ApiError as e:
        return e.response
