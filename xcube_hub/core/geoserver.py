from typing import Tuple

from geo.Geoserver import Geoserver

from xcube_hub import api
from xcube_hub.models.collection import Collection
from xcube_hub.typedefs import AnyDict


def register(user_id, subscription, headers, raising):
    geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')
    geo.create_workspace(workspace='demo')
    geo.publish_featurestore(workspace='demo', store_name='geodb', pg_table='eea-urban-atlas_DE060L1_CELLE_UA2018')
    pass


def put_collection(collection: str, database: str) -> Tuple[AnyDict, int]:
    try:
        geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')
        geo.create_workspace(workspace='demo')
        res = geo.publish_featurestore(workspace='demo', store_name='geodb', pg_table='eea-urban-atlas_DE060L1_CELLE_UA2018')
        collection = Collection()
        return api.ApiResponse.success(collection.to_dict())
    except api.ApiError as e:
        return e.response

