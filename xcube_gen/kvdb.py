import json
import os
from json import JSONDecodeError
from typing import Optional

from xcube_gen import api
from xcube_gen.xg_types import JsonObject


class _KvDBProvider:
    pass


class KvDB:
    __doc__ = \
        f"""
        A key-value pair database interface connector class (e.g. to redis)
        
        Defines abstract methods fro getting, deleting and putting key value pairs
        
        """

    provider = 'leveldb'
    validators = []

    instance = None

    def __init__(self, provider: str, **kwargs):
        if not self.instance:
            self._get_instance(provider=provider, **kwargs)

    def get(self, key) -> Optional[JsonObject]:
        """
        Get a key value
        :param key:
        :return:
        """

        res = self.instance.get(key)
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
            for validator in self.validators:
                validator(value)

            value = json.dumps(value)
            return self.instance.set(key, value)
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

        return self.instance.delete(key)

    def _get_instance(self, provider: Optional[str] = None, **kwargs) -> _KvDBProvider:
        """
        Return a database singleton.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if self.instance is None:
            if provider == 'redis':
                return _RedisKvDB(**kwargs)
            elif provider == 'leveldb':
                return _LevelDBKvDB(**kwargs)
            elif provider == 'inmemory':
                return _InMemoryKvDB(**kwargs)
            else:
                raise api.ApiError(500, f"Provider {provider} unknown.")


class _RedisKvDB(_KvDBProvider):
    __doc__ = \
        f"""
        Redis key-value pair database implementation of Kv
        
        Defines methods for getting, deleting and putting key value pairs
        
        :param host, port, db (see also https://github.com/andymccurdy/redis-py)
        Example:
        ```
            db = Kv.instance(kv_provider='redis', host='localhost', port=6379, db=0)
        ```
        """

    # noinspection PyUnresolvedReferences
    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        super().__init__()
        try:
            from redis import Redis
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import redis. Please install first.")

        host = os.getenv('XCUBE_GEN_REDIS_HOST') or host
        port = os.getenv('XCUBE_GEN_REDIS_POST') or port
        db = os.getenv('XCUBE_GEN_REDIS_DB') or db

        self._db = Redis(host=host, port=port, db=db, **kwargs)

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

        return self._db.set(key, value)

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        return self._db.delete(key)


class _LevelDBKvDB(_KvDBProvider):
    __doc__ = \
        f"""
        Redis key-value pair database implementation of Kv
        
        Defines methods for getting, deleting and putting key value pairs
        
        :param host, port, db (see also https://github.com/andymccurdy/redis-py)
        Example:
        ```
            db = Kv.instance(kv_provider='leveldb', name='/tmp/testdb/', create_if_missing=True)
        ```
        """

    def __init__(self, name: str = '/tmp/testdb/', create_if_missing=True, *args, **kwargs):
        super().__init__()
        try:
            import plyvel
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import plyvel. Please install first.")

        name = os.getenv('XCUBE_GEN_LEVELDB_NAME') or name
        create_if_missing = os.getenv('XCUBE_GEN_LEVELDB_CREATE_IF_MISSING') or create_if_missing

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


class _InMemoryKvDB(_KvDBProvider):
    __doc__ = \
        f"""
        None Cache if no Provider is given
        """

    def __init__(self, db_init: Optional[dict] = None):
        super().__init__()

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
