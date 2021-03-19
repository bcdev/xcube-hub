from xcube_hub import api
from xcube_hub.core import cate


def get_webapis():
    try:
        num_pods = cate.get_pod_count()
        return api.ApiResponse.success(num_pods)
    except api.ApiError as e:
        return e.response
