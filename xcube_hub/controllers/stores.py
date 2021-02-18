from xcube_hub import api
from xcube_hub.core.stores import get_stores_from_file


def get_stores():
    """get service info

    Get service info


    :rtype: ApiStoresResponse
    """

    try:
        stores = get_stores_from_file()
        return api.ApiResponse.success(result=stores)
    except api.ApiError as e:
        return e.response
