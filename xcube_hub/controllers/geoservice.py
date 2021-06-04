from typing import Tuple

from xcube_hub import api
from xcube_hub.geoservice import GeoService
from xcube_hub.typedefs import AnyDict


def get_collections(database_id: str) -> Tuple[AnyDict, int]:
    try:
        geo = GeoService.instance()
        collections = geo.get_layers(database_id=database_id)

        return api.ApiResponse.success(collections)
    except api.ApiError as e:
        return e.response


def get_collection(collection_id: str, database_id: str) -> Tuple[AnyDict, int]:
    try:
        geo = GeoService.instance()
        collection = geo.get_layer(collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response


def put_collection(database_id: str, body) -> Tuple[AnyDict, int]:
    try:
        geo = GeoService.instance()
        if 'collection_id' not in body:
            raise api.ApiError(400, "put_collection needs a collection_id")

        geo.publish(collection_id=body['collection_id'], database_id=database_id)

        return api.ApiResponse.success("success")
    except api.ApiError as e:
        return e.response


def delete_collection(database_id: str, collection_id: str) -> Tuple[AnyDict, int]:
    try:
        geo = GeoService.instance()
        collection = geo.unpublish(collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response

