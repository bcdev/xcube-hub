from abc import abstractmethod

import os
from typing import Optional

from xcube_gen import api


class Cache:
    __doc__ = \
        f"""
        A key-value pair database interface connector class (e.g. to redis)
        
        Defines abstract methods fro getting, deleting and putting key value pairs
        
        """

    provider = 'leveldb'

    _instance = None

    def __init__(self, **kwargs):
        pass

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        return self._instance.get(key)

    @abstractmethod
    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        return self._instance.set(key, value)

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        return self._instance.delete(key)

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def configure(cls, provider: Optional[str] = None, **kwargs) -> "Cache":
        """
        Return a database singleton.

        :param provider: Cache provider (redis, leveldb, json, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        cls.provider = provider or cls.provider
        cls.provider = os.getenv('XCUBE_GEN_CACHE_PROVIDER') or cls.provider

        if cls.provider and cls.provider != provider:
            cls._instance = None

        cls.provider = provider
        if cls._instance is None:
            if cls._instance is None:
                if cls.provider == 'redis':
                    cls._instance = RedisCache(**kwargs)
                elif cls.provider == 'leveldb':
                    cls._instance = LevelDBCache(**kwargs)
                elif cls.provider == 'json':
                    cls._instance = JsonCache(**kwargs)
                else:
                    raise api.ApiError(500, f"Provider {cls.provider} unknown.")
        return cls._instance


class RedisCache(Cache):
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


class LevelDBCache(Cache):
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
            return False

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


class JsonCache(Cache):
    __doc__ = \
        f"""
        Json key-value pair database implementation of Kv
        
        Defines methods for getting, deleting and putting key value pairs using a json file
        
        :param file
        Example:
        ```
            db = Kv.instance(kv_provider='json', '/tmp/testdb/callback.json')
        ```
        """

    def __init__(self, file_name: str = 'callback.json'):
        super().__init__()

        print("Warning: You are using the xcube-gen json cache adaptor. This adaptor is for development purposes only. "
              "For better performance use either 'redis' or 'leveldb'.")

        file_name = os.getenv('XCUBE_GEN_JSON_FILE_NAME') or file_name
        self._file_name = file_name

        try:
            import json
        except ImportError:
            raise api.ApiError(500, "Error: Cannot import json. Please install first.")

        if not os.path.isfile(self._file_name):
            with open(self._file_name, 'w') as js:
                json.dump({}, js)
                js.close()

        with open(self._file_name, 'r') as js:
            self._db = json.load(js)
            js.close()

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        if key not in self._db:
            return False

        return self._db[key]

    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        self._db[key] = value

        with open(self._file_name, 'w') as js:
            import json
            json.dump(self._db, js)
            js.close()

        return True

    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        del self._db[key]

        return True
