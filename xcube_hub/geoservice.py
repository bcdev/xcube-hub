import os
from abc import abstractmethod, ABC
from typing import Optional
from xcube_hub import api, util
from xcube_hub.models.collection import Collection


class GeoServiceBase(ABC):
    _provider = None

    @abstractmethod
    def get_layers(self, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param database_id:
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

    def get_layers(self, database_id: str) -> Optional[Collection]:
        """
        Get a key value
        :param database_id:
        :return: Collection
        """

        return self._provider.get_layers(database_id)

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
        else:
            raise api.ApiError(400, f"Provider {provider} unknown.")

    @classmethod
    def instance(cls, provider: Optional[str] = None, refresh: bool = False, use_mocker: bool = False, **kwargs)\
            -> "GeoServiceBase":
        refresh = refresh or cls._instance is None
        if refresh:
            cls._instance = GeoService(provider=provider, **kwargs)

        return cls._instance


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

    def __init__(self, url='localhost', username='admin', password='geoserver', **kwargs):
        super().__init__()
        try:
            from geo.Geoserver import Geoserver
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import Geoserver. Please install first.")

        url = os.getenv('XCUBE_HUB_GEOSERVER_URL') or url
        username = os.getenv('XCUBE_HUB_GEOSERVER_USERNAME') or username
        password = os.getenv('XCUBE_HUB_GEOSERVER_PASSWORD') or password

        self._geo = Geoserver(url, username=username, password=password, **kwargs)
# https://stage.xcube-geodb.brockmann-consult.de/geoserver/demo/wms/kml?layers=demo%3Aeea-urban-atlas_TR021L1_NEVSEHIR_UA2018
# https://stage.xcube-geodb.brockmann-consult.de/geoserver/demo/wms?service=WMS&version=1.1.0&request=GetMap&layers=demo%3Aeea-urban-atlas_TR021L1_NEVSEHIR_UA2018&bbox=6420649.0%2C2053709.75%2C6457151.0%2C2085892.25&width=768&height=677&srs=EPSG%3A3035&styles=&format=application/openlayers

    def get_layers(self, database_id: str) -> Collection:
        """
        Get a key value
        :param database_id:
        :return: Collection
        """

        try:
            return self._geo.get_layers(workspace=database_id)
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
            return self._geo.get_layer(layer_name=collection_id, workspace=database_id)
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
                host = util.maybe_raise_for_env("XCUBE_HUB_POSTGIS_HOST")
                pg_user = util.maybe_raise_for_env("XCUBE_HUB_POSTGIS_USER")
                pg_password = util.maybe_raise_for_env("XCUBE_HUB_POSTGIS_PASSWORD")
                self._geo.create_featurestore(store_name=database_id,
                                              workspace=database_id,
                                              host=host,
                                              port=5432,
                                              db='geodb',
                                              pg_user=pg_user,
                                              pg_password=pg_password)

            self._geo.publish_featurestore(workspace=database_id, store_name=database_id, pg_table=collection_id)
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
            return self._geo.delete_layer(layer_name=collection_id, workspace=database_id)
        except Exception as e:
            raise api.ApiError(400, str(e))

