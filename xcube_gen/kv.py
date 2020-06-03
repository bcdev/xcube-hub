import threading
from abc import abstractmethod


class Kv:
    _instance_lock = threading.Lock()
    _instance = None

    def __init__(self, **kwargs):
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

        :param kwargs: Keyword-arguments passed to ``Database`` constructor.
        """
        if cls._instance is None:
            cls._instance_lock.acquire()
            if cls._instance is None:
                if kv_provider == 'redis':
                    cls._instance = RedisKv(**kwargs)
                elif kv_provider == 'leveldb':
                    cls._instance = LevelDBKv(**kwargs)
                else:
                    raise KvError(f"Provider {kv_provider} not known.")
            cls._instance_lock.release()
        return cls._instance


class RedisKv(Kv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from redis import Redis
        self._db = Redis(**kwargs)

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            import plyvel
        except ImportError:
            raise KvError("Error: Cannot import plyvel. Please install first.")

        self._db = plyvel.DB('/tmp/testdb/', create_if_missing=True)

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

        return self._db.put(key, value)

    @abstractmethod
    def delete(self, key):
        """
        Delete a key
        :param key:
        :return:
        """

        return self._db.delete(key)


class KvError(BaseException):
    """
    Raised by methods of :class:`Kv`.
    """
    pass
