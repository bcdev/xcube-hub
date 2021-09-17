from xcube_hub import api
from xcube_hub.core import xcube


def create():
    try:
        xcube.create(user_id='dfsv', cfg={})
        return api.ApiResponse.success('SUCCESS')
    except api.ApiError as e:
        return e.response


def delete():
    try:
        xcube.delete()
        return api.ApiResponse.success('SUCCESS')
    except api.ApiError as e:
        return e.response
