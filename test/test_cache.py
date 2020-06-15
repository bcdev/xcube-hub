import unittest
from unittest import mock
from unittest.mock import patch
from xcube_gen import api
from xcube_gen.cache import Cache


class TestCache(unittest.TestCase):
    def test_instance(self):
        Cache._instance = None
        inst = Cache.configure(provider='json')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache.JsonCache'>")

        Cache._instance = None
        inst = Cache.configure(provider='leveldb', name='/tmp/testinstance')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache.LevelDBCache'>")

        Cache._instance = None
        inst = Cache.configure(provider='redis')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache.RedisCache'>")

        Cache._instance = None
        with self.assertRaises(api.ApiError) as e:
            Cache.configure('jso')

        self.assertEqual("Provider jso unknown.", str(e.exception))


class TestRedisCache(unittest.TestCase):
    def setUp(self) -> None:
        self._mock_set_patch = patch('redis.Redis.set')
        self._mock_set = self._mock_set_patch.start()
        self._mock_set.return_value = True

        self._mock_get_patch = patch('redis.Redis.get')
        self._mock_get = self._mock_get_patch.start()

        self._mock_delete_patch = patch('redis.Redis.delete')
        self._mock_delete = self._mock_delete_patch.start()
        self._mock_delete.return_value = True

        Cache.configure(provider='redis')
        self._db = Cache()

    def tearDown(self) -> None:
        self._mock_set_patch.stop()
        self._mock_get_patch.stop()
        self._mock_delete_patch.stop()

    def test_get(self):
        self._mock_get.return_value = None

        res = self._db.get('äpasoCacheäp')
        self.assertFalse(res)

        self._mock_get.return_value = 'value'
        res = self._db.get('key')
        self.assertEqual('value', res)

    def test_set(self):
        self._mock_set.return_value = True

        res = self._db.set('testSet', 'testValue')
        self.assertTrue(res)

        self._mock_get.return_value = 'testValue'
        res = self._db.get('testSet')
        self.assertEqual('testValue', res)

    def test_delete(self):
        self._mock_delete.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        self._mock_get.return_value = None
        res = self._db.get('key')
        self.assertFalse(res)


class TestLevelDbCache(unittest.TestCase):
    def setUp(self) -> None:
        Cache.configure(provider='leveldb', name='/tmp/testleveldb', create_if_missing=True)

        self._db = Cache()

        self._db.set('key', 'value')

    @mock.patch('plyvel.DB')
    def test_get(self, mock_db):
        mock_db.get.return_value = True
        res = self._db.get('äpasoCacheäp')
        self.assertFalse(res)

        res = self._db.get('key')
        self.assertEqual('value', res)

    @mock.patch('plyvel.DB')
    def test_set(self, mock_db):
        mock_db.set.return_value = True
        res = self._db.set('testSet', 'testValue')
        self.assertTrue(res)

        mock_db.get.return_value = 'testValue'
        res = self._db.get('testSet')
        self.assertEqual('testValue', res)

    @mock.patch('plyvel.DB')
    def test_delete(self, mock_db):
        mock_db.delete.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        res = self._db.get('key')
        mock_db.get.return_value = False
        self.assertFalse(res)


class TestJsonCache(unittest.TestCase):
    def setUp(self) -> None:
        Cache._instance = None
        Cache.configure(provider='json')
        self._db = Cache()
        self._db._instance._db = {'key': 'value', 'key2': 'value2'}

    def test_get(self):
        res = self._db.get('äpasoCacheäp')
        self.assertFalse(res)

        res = self._db.get('key')
        self.assertEqual('value', res)

    def test_put(self):
        res = self._db.set('testSet', 'testValue')
        self.assertTrue(res)

        res = self._db.get('testSet')
        self.assertEqual('testValue', res)

    def test_delete(self):
        res = self._db.delete('key2')
        self.assertTrue(res)

        res = self._db.get('key2')
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()
