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
    def configure(cls, provider: Optional[str] = None, **kwargs) -> Optional["Cache"]:
        """
        Return a database singleton.

        :param provider: Cache provider (redis, leveldb, default leveldb)
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """

        if cls.provider and cls.provider != provider:
            cls._instance = None

        cls.provider = provider or cls.provider
        cls.provider = os.getenv('XCUBE_GEN_CACHE_PROVIDER') or cls.provider

        if cls._instance is None:
            if cls._instance is None:
                if cls.provider == 'redis':
                    cls._instance = RedisCache(**kwargs)
                elif cls.provider == 'leveldb':
                    cls._instance = LevelDBCache(**kwargs)
                elif cls.provider == 'inmemory':
                    cls._instance = InMemoryCache(**kwargs)
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


class InMemoryCache(Cache):
    __doc__ = \
        f"""
        None Cache if no Provider is given
        """

    def __init__(self, db_init: Optional[dict] = None):
        super().__init__()
        self._db = db_init or dict()

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
