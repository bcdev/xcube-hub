import threading
from abc import abstractmethod

import os


class Kv:
    __doc__ = \
        f"""
        A key-value pair database interface connector class (e.g. to redis)
        
        Defines abstract methods fro getting, deleting and putting key value pairs
        
        """

    _instance_lock = threading.Lock()
    _instance_type = None
    _instance = None

    def __init__(self):
        self._db = None

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

    @classmethod
    def instance(cls, kv_provider: str, **kwargs) -> "Kv":
        """
        Return a database singleton.

        :param kv_provider: KV Provider ('redis', 'leveldb')
        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """
        if cls._instance_type and cls._instance_type != kv_provider:
            cls._instance = None
        cls._instance_type = kv_provider
        if cls._instance is None:
            cls._instance_lock.acquire()
            if cls._instance is None:
                if kv_provider == 'redis':
                    cls._instance = RedisKv(**kwargs)
                elif kv_provider == 'leveldb':
                    cls._instance = LevelDBKv(**kwargs)
                elif kv_provider == 'json':
                    cls._instance = JsonKv(**kwargs)
                else:
                    raise KvError(f"Provider {kv_provider} not known.")
            cls._instance_lock.release()
        return cls._instance


class RedisKv(Kv):
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

    def __init__(self, host='localhost', port=6379, db=0, **kwargs):
        super().__init__()
        from redis import Redis
        self._db = Redis(host=host, port=port, db=db, **kwargs)

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        return self._db.get(key)

    @abstractmethod
    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        return self._db.set(key, value)

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        return self._db.delete(key)


class LevelDBKv(Kv):
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
            raise KvError("Error: Cannot import plyvel. Please install first.")

        self._db = plyvel.DB(name=name, create_if_missing=True)

    def get(self, key):
        """
        Get a key value
        :param key:
        :return:
        """

        if not self._db.get(str.encode(key)):
            return False

        return self._db.get(str.encode(key)).decode()

    @abstractmethod
    def set(self, key, value):
        """
        Set a key value
        :param value:
        :param key:
        :return:
        """

        self._db.put(str.encode(key), str.encode(value))

        return True

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        self._db.delete(str.encode(key))

        return True


class JsonKv(Kv):
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

        print("Warning: You are using the json adaptor. This adaptor is for development only. For better performance"
              " use either redis or leveldb. Both need to be installed.")
        self._file_name = file_name

        try:
            import json
        except ImportError:
            raise KvError("Error: Cannot import json. Please install first.")

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

    @abstractmethod
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

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        del self._db[key]

        return True


class KvError(BaseException):
    """
    Raised by methods of :class:`Kv`.
    """
    pass
