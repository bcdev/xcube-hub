import os
from typing import Tuple, Dict, Optional

import requests
from requests import HTTPError

from xcube_hub import api, util
from xcube_hub.controllers.authorization import _get_claim_from_token
from xcube_hub.geoservice import GeoService
from xcube_hub.typedefs import AnyDict


def _maybe_raise_for_service_silent():
    cate_silent = os.getenv("GEOSERVICE_SILENT", default=None)

    if cate_silent == '1':
        raise api.ApiError(422, "Geoservice resources are switched off on this service")


def _raise_for_no_access(database_id, geodb_user, token):
    geodb_server_url = util.maybe_raise_for_env('GEODB_POSTGREST_REST_URL')
    url = f"{geodb_server_url}/rpc/geodb_list_databases"

    r = requests.post(url=url, headers={'Authorization': f'Bearer {token}'})

    try:
        r.raise_for_status()
    except HTTPError as e:
        raise api.ApiError(400, str(e))

    res = r.json()

    dbs = res[0]['src']

    if dbs is None:
        raise api.ApiError(404, f'Database {database_id} not found.')

    success = False

    for db in dbs:
        if db['name'] == database_id and db['owner'] == geodb_user:
            success = True

    if success is False:
        raise api.ApiError(401, f'The user {geodb_user} does not have access to database {database_id}')


def get_all_collections(token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        _maybe_raise_for_service_silent()
        geo = GeoService.instance()
        collections = geo.get_all_layers(fmt='geopandas')

        return api.ApiResponse.success(collections)
    except api.ApiError as e:
        return e.response


def get_collections(token_info: Dict, database_id: Optional[str] = None) -> Tuple[AnyDict, int]:
    try:
        _maybe_raise_for_service_silent()
        token = token_info['token']
        geodb_user = _get_claim_from_token(token=token, tgt="https://geodb.brockmann-consult.de/dbrole")

        if database_id is not None and database_id != 'all':
            _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        database_id = None if database_id == 'all' else database_id
        collections = geo.get_layers(user_id=geodb_user, database_id=database_id, fmt='geopandas')

        return api.ApiResponse.success(collections)
    except api.ApiError as e:
        return e.response


def get_collection(collection_id: str, database_id: str, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        _maybe_raise_for_service_silent()
        token = token_info['token']
        geodb_user = _get_claim_from_token(token=token, tgt="https://geodb.brockmann-consult.de/dbrole")

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        collection = geo.get_layer(user_id=geodb_user, collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response


def put_collection(database_id: str, body, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        _maybe_raise_for_service_silent()
        token = token_info['token']
        geodb_user = _get_claim_from_token(token=token, tgt="https://geodb.brockmann-consult.de/dbrole")

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        if 'collection_id' not in body:
            raise api.ApiError(400, "put_collection needs a collection_id")

        res = geo.publish(user_id=geodb_user, collection_id=body['collection_id'], database_id=database_id)

        return api.ApiResponse.success(res.to_dict())
    except api.ApiError as e:
        return e.response


def delete_collection(database_id: str, collection_id: str, token_info: Dict) -> Tuple[AnyDict, int]:
    try:
        _maybe_raise_for_service_silent()
        token = token_info['token']
        geodb_user = _get_claim_from_token(token=token, tgt="https://geodb.brockmann-consult.de/dbrole")

        _raise_for_no_access(database_id=database_id, geodb_user=geodb_user, token=token)

        geo = GeoService.instance()
        collection = geo.unpublish(user_id=geodb_user, collection_id=collection_id, database_id=database_id)

        return api.ApiResponse.success(collection)
    except api.ApiError as e:
        return e.response

