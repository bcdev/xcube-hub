from xcube_hub import api
from xcube_hub.core import services


def get_services():
    try:
        svcs = services.get_services()
        return api.ApiResponse.success(svcs)
    except api.ApiError as e:
        return e.response


def get_service(service_id: str):
    try:
        svcs = services.get_service(service_id=service_id)
        return api.ApiResponse.success(svcs)

    except api.ApiError as e:
        return e.response


def put_subscription_to_service(service_id: str, user: str):
    # create User
    # create client
    # register to service if necessary
    # gather into and return
    pass


def get_subscription_from_service(service_id: str, user: str):
    pass


def delete_subscription_from_service(service_id: str, user: str):
    pass
