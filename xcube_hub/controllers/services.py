from typing import Dict

from xcube_hub import api
from xcube_hub.subscription_api import SubscriptionApi
from xcube_hub.core import services
from xcube_hub.models.subscription import Subscription
from xcube_hub.typedefs import JsonObject


def get_services():
    try:
        svcs = services.get_services()
        return api.ApiResponse.success(svcs)
    except api.ApiError as e:
        return e.response


def put_subscription_to_service(service_id: str, body: JsonObject, token_info: Dict):
    try:
        auth_api = SubscriptionApi.instance(iss=token_info['iss'], token=token_info['token'])
        subscription = Subscription.from_dict(body)
        res = auth_api.add_subscription(service_id=service_id, subscription=subscription)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response


def get_subscription_from_service(service_id: str, subscription_id, token_info: Dict):
    try:
        auth_api = SubscriptionApi.instance(iss=token_info['iss'], token=token_info['token'])
        subscription = auth_api.get_subscription(service_id=service_id, subscription_id=subscription_id)
        return api.ApiResponse.success(subscription.to_dict())
    except api.ApiError as e:
        return e.response


def delete_subscription_from_service(service_id: str, subscription_id, token_info: Dict):
    try:
        auth_api = SubscriptionApi.instance(iss=token_info['iss'], token=token_info['token'])
        res = auth_api.delete_subscription(service_id=service_id, subscription_id=subscription_id)
        return api.ApiResponse.success(res)
    except api.ApiError as e:
        return e.response
