import json
import os
from abc import abstractmethod, ABC
from json import JSONDecodeError
from typing import Optional, Any
from xcube_hub import api
from xcube_hub.typedefs import JsonObject


class KeyValueStore(ABC):
    @abstractmethod
    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

    @abstractmethod
    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """


class KeyValueDatabase(KeyValueStore):
    f"""
    A key-value pair database interface connector class (e.g. to redis)
    
    Defines abstract methods fro getting, deleting and putting key value pairs
    
    """

    _instance = None

    def __init__(self, provider: str, use_mocker: bool = False, **kwargs):
        use_mocker = os.getenv("XCUBE_GEN_API_USE_KV_MOCK") or use_mocker
        self._provider = self._new_db(provider=provider, use_mocker=use_mocker, **kwargs)

    def get(self, key) -> Optional[JsonObject]:
        """
        Get a key value
        :param key:
        :return:
        """

        res = self._provider.get(key)
        if not res:
            return res

        try:
            if isinstance(res, str):
                return json.loads(res)
            else:
                return res
        except JSONDecodeError as e:
            raise api.ApiError(401, "System error (Cache): Cash contained invalid json " + str(e))
        except ValueError as e:
            raise api.ApiError(401, "System error (Cache): Cash contained invalid json " + str(e))

    def set(self, key, value: JsonObject):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        try:
            value = json.dumps(value)
            return self._provider.set(key, value)
        except JSONDecodeError as e:
            raise api.ApiError(401, "System error (Cache): Cash contained invalid json " + str(e))
        except ValueError as e:
            raise api.ApiError(401, "System error (Cache): Cash contained invalid json " + str(e))

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        return self._provider.delete(key)

    def _new_db(self, provider: Optional[str] = None, use_mocker: bool = False, **kwargs) -> "KeyValueStore":
        """
        Return a new database instance.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if provider == 'redis':
            return _RedisKvDB(use_mocker=use_mocker, **kwargs)
        elif provider == 'leveldb':
            return _LevelDBKvDB(use_mocker=use_mocker, **kwargs)
        elif provider == 'inmemory':
            return _InMemoryKvDB(use_mocker=use_mocker, **kwargs)
        else:
            raise api.ApiError(401, f"Provider {provider} unknown.")

    @classmethod
    def instance(cls, provider: Optional[str] = None, refresh: bool = False, use_mocker: bool = False, **kwargs)\
            -> "KeyValueDatabase":
        refresh = refresh or cls._instance is None
        if refresh:
            provider = provider or 'inmemory'
            cls._instance = KeyValueDatabase(provider=provider, use_mocker=use_mocker, **kwargs)

        return cls._instance


class _RedisKvDB(KeyValueStore):
    f"""
    Redis key-value pair database implementation of KeyValueStore
    
    Defines methods for getting, deleting and putting key value pairs
    
    :param host, port, db (see also https://github.com/andymccurdy/redis-py)
    Example:
    ```
        db = KeyValueDatabase.instance(provider='redis', host='localhost', port=6379, db=0)
    ```
    """

    def __init__(self, host='xcube-gen-stage-redis', port=6379, db=0, use_mocker: bool = False, **kwargs):
        super().__init__()
        try:
            from redis import Redis
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import redis. Please install first.")

        host = os.getenv('XCUBE_GEN_REDIS_HOST') or host
        port = os.getenv('XCUBE_GEN_REDIS_POST') or port
        db = os.getenv('XCUBE_GEN_REDIS_DB') or db

        if use_mocker is True or use_mocker == 1:
            self._db = _KvDBMocker()
        else:
            self._db = Redis(host=host, port=port, db=db, **kwargs)

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """
        # noinspection PyUnresolvedReferences
        try:
            val = self._db.get(key)
        except redis.exceptions.ConnectionError:
            raise api.ApiError(400, "System Error: redis cache not ready.")
        if isinstance(val, bytes):
            val = val.decode('utf-8')
        return val

    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        # noinspection PyUnresolvedReferences
        try:
            return self._db.set(key, value)
        except redis.exceptions.ConnectionError:
            raise api.ApiError(400, "System Error: redis cache not ready.")

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        # noinspection PyUnresolvedReferences
        try:
            return self._db.delete(key)
        except redis.exceptions.ConnectionError:
            raise api.ApiError(400, "System Error: redis cache not ready.")


class _LevelDBKvDB(KeyValueStore):
    f"""
    Redis key-value pair database implementation of KeyValueStore
    
    Defines methods for getting, deleting and putting key value pairs
    
    :param host, port, db (see also https://github.com/andymccurdy/redis-py)
    Example:
    ```
        db = KeyValueDatabase.instance(provider='leveldb', name='/tmp/testdb/', create_if_missing=True)
    ```
    """

    def __init__(self, name: str = '/tmp/testdb/', create_if_missing=True, use_mocker: bool = False, *args, **kwargs):
        super().__init__()
        try:
            import plyvel
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import plyvel. Please install first.")

        name = os.getenv('XCUBE_GEN_LEVELDB_NAME') or name
        create_if_missing = os.getenv('XCUBE_GEN_LEVELDB_CREATE_IF_MISSING') or create_if_missing

        if use_mocker is True or use_mocker == 1:
            self._db = _KvDBMocker()
        else:
            self._db = plyvel.DB(name=name, create_if_missing=create_if_missing, *args, **kwargs)

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        if not self._db.get(str.encode(key)):
            return None

        return self._db.get(str.encode(key)).decode()

    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        self._db.put(str.encode(key), str.encode(value))

        return True

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        self._db.delete(str.encode(key))

        return True


class _InMemoryKvDB(KeyValueStore):
    """
    InMemory key-value pair database implementation of KeyValueStore.

    Defines methods for getting, deleting and putting key value pairs

    :param db_init, use_mocker
    Example:
    ```
        db = KeyValueDatabase.instance(provider='inmemory')
    ```
    """

    def __init__(self, db_init: Optional[dict] = None, use_mocker: bool = False):
        super().__init__()

        if use_mocker is True or use_mocker == 1:
            self._db = _KvDBMocker()
        else:
            self._db = dict()

        if db_init:
            for k, v in db_init.items():
                self.set(k, json.dumps(v))

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        return self._db.get(key)

    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """
        self._db[key] = value

        return True

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        if key in self._db:
            del self._db[key]
            return True

        return False


class _KvDBMocker:
    """
    Mocker for unittests
    """
    return_value: Optional[Any] = None

    def get(self, *args, **kwargs):
        return self.return_value

    def set(self, *args, **kwargs):
        return self.return_value

    def delete(self, *args, **kwargs):
        return self.return_value

    def put(self, *args, **kwargs):
        return self.return_value
