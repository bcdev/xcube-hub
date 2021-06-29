import os
from abc import abstractmethod, ABC
from typing import Optional, Any, Dict, Sequence

import requests

from xcube_hub import api
from xcube_hub.models.collection import Collection


class GeoServiceBase(ABC):
    _provider = None

    @abstractmethod
    def get_layers(self, database_id: str, fmt: str) -> dict:
        """
        Get a key value
        :param database_id:
        :param fmt: return format [geopandas, json]
        :return: Collection
        """

    @abstractmethod
    def get_layer(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param collection_id:
        :param database_id:
        :return: Collection
        """

    @abstractmethod
    def publish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Set a key value
        :param collection_id:
        :param database_id:
        :return: Collection
        """

    @abstractmethod
    def unpublish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Delete a key
        :param collection_id:
        :param database_id:
        :return: Collection
        """


class GeoService(GeoServiceBase):
    f"""
    A key-value pair database interface connector class (e.g. to redis)
    
    Defines abstract methods fro getting, deleting and putting key value pairs
    
    """

    _instance = None

    def __init__(self, provider: str, **kwargs):
        self._provider = self._new_service(provider=provider, **kwargs)

    def get_layers(self, database_id: str, fmt: str) -> dict:
        """
        Get a key value
        :param database_id:
        :param fmt: return format [geopandas, json]
        :return: Collection
        """

        return self._provider.get_layers(database_id, fmt)

    def get_layer(self, collection_id, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param database_id:
        :param collection_id:
        :return: Optional[Collection]
        """

        return self._provider.get_layer(collection_id, database_id)

    def publish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Set a key value
        :param collection_id:
        :param database_id:
        :return: Optional[Collection]
        """

        return self._provider.publish(collection_id, database_id)

    def unpublish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Set a key value
        :param collection_id:
        :param database_id:
        :return: Optional[Collection]
        """

        return self._provider.unpublish(collection_id, database_id)

    # noinspection PyMethodMayBeStatic
    def _new_service(self, provider: Optional[str] = None, **kwargs) -> "GeoServiceBase":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if provider == 'geoserver':
            return _GeoServer(**kwargs)
        elif provider == 'mock':
            return _GeoServiceMock()
        else:
            raise api.ApiError(400, f"Provider {provider} unknown.")

    @classmethod
    def instance(cls, provider: Optional[str] = None, refresh: bool = False, **kwargs) \
            -> "GeoServiceBase":
        refresh = refresh or cls._instance is None
        if refresh:
            cls._instance = GeoService(provider=provider, **kwargs)

        return cls._instance


def _raise_for_none(name: str, value: Any):
    if value is None:
        raise api.ApiError(400, f"Value {name} is None")


class _GeoServer(GeoServiceBase):
    f"""
    Redis key-value pair database implementation of KeyValueStore
    
    Defines methods for getting, deleting and putting key value pairs
    
    :param host, port, db (see also https://github.com/andymccurdy/redis-py)
    Example:
    ```
        db = KeyValueDatabase.instance(provider='redis', host='localhost', port=6379, db=0)
    ```
    """

    def __init__(self,
                 url: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 pg_user: Optional[str] = None,
                 pg_password: Optional[str] = None,
                 pg_host: Optional[str] = None,
                 pg_db: Optional[str] = None,
                 **kwargs):
        super().__init__()
        try:
            from geo.Geoserver import Geoserver
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import Geoserver. Please install first.")

        self._url = url or os.getenv('XCUBE_HUB_GEOSERVER_URL')
        self._username = username or os.getenv('XCUBE_HUB_GEOSERVER_USERNAME')
        self._password = password or os.getenv('XCUBE_HUB_GEOSERVER_PASSWORD')
        self._pg_host = pg_host or os.getenv("XCUBE_HUB_POSTGIS_HOST")
        self._pg_user = pg_user or os.getenv("XCUBE_HUB_POSTGIS_USER")
        self._pg_password = pg_password or os.getenv("XCUBE_HUB_POSTGIS_PASSWORD")
        self._pg_db = pg_db or os.getenv("XCUBE_HUB_POSTGIS_DB")

        self._geo = Geoserver(self._url, username=self._username, password=self._password)

        for prop, value in vars(self).items():
            _raise_for_none(prop, value)

    def get_layers(self, database_id: str, fmt: str = 'geopandas') -> Sequence[Dict]:
        """
        Get a key value
        :param fmt: return format [geopandas, json]
        :param database_id:
        :return: Collection
        """

        try:
            res = self._geo.get_layers(workspace=database_id)
            if res['layers'] == '':
                raise api.ApiError(404, f'No collections found in database {database_id}')

            layers = res['layers']['layer']

            if fmt == 'geopandas':
                layers_res = {
                    "collection_id": [],
                    "database": [],
                    "default_style": [],
                    "geojson_url": [],
                    "href": [],
                    "name": [],
                    "preview_url": [],
                    "wfs_url": []
                }

                for layer in layers:
                    name = layer['name']
                    collection_id = name.replace(database_id + '_', '')
                    collection = self.get_layer(collection_id=collection_id, database_id=database_id)
                    for k, v in collection.to_dict().items():
                        layers_res[k].append(v)
            else:
                layers_res = []
                for layer in layers:
                    name = layer['name']
                    collection_id = name.replace(database_id + '_', '')
                    collection = self.get_layer(collection_id=collection_id, database_id=database_id)
                    layers_res.append(collection.to_dict())

                if len(layers_res) == 0:
                    raise api.ApiError(404, f'No collections found in database {database_id}')

            return layers_res
        except Exception as e:
            raise api.ApiError(400, str(e))

    def get_layer(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param collection_id:
        :param database_id:
        :return: Optional[Collection]
        """

        try:
            layer_name = database_id + '_' + collection_id
            try:
                layer = self._geo.get_layer(layer_name=layer_name, workspace=database_id)
                if 'get_layer error' in layer:
                    raise api.ApiError(404, f'Cannot find collection {collection_id} in database {database_id}')
            except Exception as e:
                raise api.ApiError(400, str(e))

            url = layer['layer']['resource']['href']
            r = requests.get(url, auth=(self._username, self._password))
            layer_wms = r.json()
            bbox = layer_wms['featureType']['nativeBoundingBox']
            srs = layer_wms['featureType']['srs']

            preview_url = f"{self._url}/{database_id}/wms?service=WMS&version=1.1.0&request=GetMap&" \
                          f"layers={database_id}:{layer_name}&" \
                          f"bbox={bbox['minx']},{bbox['miny']},{bbox['maxx']},{bbox['maxy']}&" \
                          f"width=690&height=768&srs={srs}&styles=&format=application/openlayers"

            geojson_url = f"{self._url}/{database_id}/ows?service=WFS&version=1.0.0&request=GetFeature&" \
                          f"typeName={database_id}:{layer_name}&maxFeatures=10&outputFormat=application/json"

            wfs_url = f"{self._url}/{database_id}/ows?service=WFS&" \
                      f"version=1.0.0&" \
                      f"request=GetFeature&" \
                      f"typeName={database_id}%3A{layer_name}&maxFeatures=10&" \
                      f"outputFormat=application%2Fvnd.google-earth.kml%2Bxml"

            collection = Collection(
                preview_url=preview_url,
                collection_id=collection_id,
                database=database_id,
                name=collection_id.replace(database_id, ''),
                geojson_url=geojson_url,
                wfs_url=wfs_url
            )

            return collection

        except Exception as e:
            raise api.ApiError(400, str(e))

    def publish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Set a key value
        :param collection_id:
        :param database_id:
        :return: Optional[Collection]
        """

        try:
            workspace = self._geo.get_workspace(workspace=database_id)
            if workspace is None:
                self._geo.create_workspace(workspace=database_id)

                self._geo.create_featurestore(store_name=database_id,
                                              workspace=database_id,
                                              host=self._pg_host,
                                              port=5432,
                                              db=self._pg_db,
                                              pg_user=self._pg_user,
                                              pg_password=self._pg_password)

            pg_table = database_id + '_' + collection_id
            self._geo.publish_featurestore(workspace=database_id, store_name=database_id, pg_table=pg_table)
            return self.get_layer(collection_id=collection_id, database_id=database_id)
        except Exception as e:
            raise api.ApiError(400, str(e))

    def unpublish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Delete a key
        :param collection_id:
        :param database_id:
        :return:
        """

        try:
            collection = self.get_layer(collection_id=collection_id, database_id=database_id)
            layer_name = database_id + '_' + collection_id
            self._geo.delete_layer(layer_name=layer_name, workspace=database_id)
            return collection
        except Exception as e:
            raise api.ApiError(400, str(e))


class _GeoServiceMock(GeoServiceBase):
    def __init__(self):
        super().__init__()

    def get_layers(self, database_id: str, fmt: str) -> dict:
        """
        Get a key value
        :param database_id:
        :return: Collection
        """

        return {}

    def get_layer(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param collection_id:
        :param database_id:
        :return: Collection
        """

        return None

    def publish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Set a key value
        :param collection_id:
        :param database_id:
        :return: Collection
        """

        return None

    def unpublish(self, collection_id: str, database_id: str) -> Optional[Collection]:
        """
        Delete a key
        :param collection_id:
        :param database_id:
        :return: Collection
        """

        return None
