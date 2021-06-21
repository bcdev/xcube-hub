from typing import Tuple, Dict

import requests

from xcube_hub import api, util
from xcube_hub.geoservice import GeoService
from xcube_hub.typedefs import AnyDict


def _raise_for_no_access(database_id, geodb_user, token):
    geodb_server_url = util.maybe_raise_for_env('GEODB_SERVER_URL')
    url = f"{geodb_server_url}/rpc/geodb_list_databases"

    r = requests.post(url=url, headers={'Authorization': f'Bearer {token}'})

    res = r.json()

    dbs = res[0]['src']

    success = False

    for db in dbs:
        if db['name'] == database_id and db['owner'] == geodb_user:
            success = True

    if success is False:
        raise api.ApiError(401, f'The user {geodb_user} does not have access to database {database_id}')


def get_collections(database_id: str, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        token = token_info['token']
        geodb_user = token_info['geodb_user']

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)
        geo = GeoService.instance()
        collections = geo.get_layers(database_id=database_id, fmt='geopandas')

        return api.ApiResponse.success(collections)
    except api.ApiError as e:
        return e.response


def get_collection(collection_id: str, database_id: str, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        token = token_info['token']
        geodb_user = token_info['geodb_user']

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        collection = geo.get_layer(collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response


def put_collection(database_id: str, body, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        token = token_info['token']
        geodb_user = token_info['geodb_user']

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        if 'collection_id' not in body:
            raise api.ApiError(400, "put_collection needs a collection_id")

        res = geo.publish(collection_id=body['collection_id'], database_id=database_id)

        return api.ApiResponse.success(res.to_dict())
    except api.ApiError as e:
        return e.response


def delete_collection(database_id: str, collection_id: str, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        token = token_info['token']
        geodb_user = token_info['geodb_user']

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        collection = geo.unpublish(collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response

