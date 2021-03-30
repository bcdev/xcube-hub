from xcube_hub import api
from xcube_hub.auth_api import AuthApi
from xcube_hub.core import services
from xcube_hub.models.subscription import Subscription
from xcube_hub.typedefs import JsonObject


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


def put_subscription_to_service(service_id: str, subscription: JsonObject) -> Subscription:
    try:
        auth_api = AuthApi.instance()
        subscription = Subscription.from_dict(subscription)
        return auth_api.add_subscription(service_id=service_id, subscription=subscription)
    except api.ApiError as e:
        return e.response


def get_subscription_from_service(service_id: str, subscription_id):
    try:
        auth_api = AuthApi.instance()
        auth_api.get_subscription(service_id=service_id, subscription_id=subscription_id)
    except api.ApiError as e:
        return e.response


def delete_subscription_from_service(service_id: str, subscription_id):
    try:
        auth_api = AuthApi.instance()
        auth_api.delete_subscription(service_id=service_id, subscription_id=subscription_id)
    except api.ApiError as e:
        return e.response
