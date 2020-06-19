import unittest
from unittest import mock
from unittest.mock import patch
from xcube_gen import api
from xcube_gen.kvdb import KvDB


class TestCache(unittest.TestCase):
    def test_instance(self):
        KvDB._instance = None
        inst = KvDB._get_instance(provider='inmemory')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache._InMemoryCache'>")

        KvDB.instance = None
        inst = KvDB._get_instance(provider='leveldb', name='/tmp/testinstance')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache._LevelDBCache'>")

        KvDB.instance = None
        inst = KvDB._get_instance(provider='redis')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.cache._RedisCache'>")

        KvDB.instance = None
        with self.assertRaises(api.ApiError) as e:
            KvDB._get_instance('jso')

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

        KvDB._get_instance(provider='redis')
        self._db = KvDB()

    def tearDown(self) -> None:
        self._mock_set_patch.stop()
        self._mock_get_patch.stop()
        self._mock_delete_patch.stop()

    def test_get(self):
        self._mock_get.return_value = None

        res = self._db.get('äpasoCacheäp')
        self.assertIsNone(res)

        self._mock_get.return_value = {'value': 'testValue'}
        res = self._db.get('key')
        self.assertEqual({'value': 'testValue'}, res)

    def test_set(self):
        self._mock_set.return_value = True

        res = self._db.set('testSet', {'value': 'testValue'})
        self.assertTrue(res)

        self._mock_get.return_value = {'value': 'testValue'}
        res = self._db.get('testSet')
        self.assertEqual({'value': 'testValue'}, res)

    def test_delete(self):
        self._mock_delete.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        self._mock_get.return_value = None
        res = self._db.get('key')
        self.assertFalse(res)


class TestLevelDbCache(unittest.TestCase):
    def setUp(self) -> None:
        KvDB._get_instance(provider='leveldb', name='/tmp/testleveldb', create_if_missing=True)

        self._db = KvDB()

        self._db.set('key', {'value': 'value'})

    @mock.patch('plyvel.DB')
    def test_get(self, mock_db):
        mock_db.get.return_value = True
        res = self._db.get('äpasoCacheäp')
        self.assertIsNone(res)

        res = self._db.get('key')
        self.assertEqual({'value': 'value'}, res)

    @mock.patch('plyvel.DB')
    def test_set(self, mock_db):
        mock_db.set.return_value = True
        res = self._db.set('testSet',  {'value': 'testValue'})
        self.assertTrue(res)

        mock_db.get.return_value = {'value': 'testValue'}
        res = self._db.get('testSet')
        self.assertEqual({'value': 'testValue'}, res)

    @mock.patch('plyvel.DB')
    def test_delete(self, mock_db):
        mock_db.delete.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        res = self._db.get('key')
        mock_db.get.return_value = False
        self.assertFalse(res)


class TestInMemoryCache(unittest.TestCase):
    def setUp(self) -> None:
        KvDB.instance = None
        KvDB._get_instance(provider='inmemory', db_init={'key': {'value': 'value'}, 'key2': {'value2': 'value2'}})
        self._cache = KvDB()

    def test_get(self):
        res = self._cache.get('äpasoCacheäp')
        self.assertIsNone(res)

        res = self._cache.get('key')
        self.assertEqual({'value': 'value'}, res)

    def test_set(self):
        res = self._cache.set('testSet', {'value': 'testValue'})
        self.assertTrue(res)

        res = self._cache.get('testSet')
        self.assertEqual({'value': 'testValue'}, res)

    def test_delete(self):
        res = self._cache.delete('key2')
        self.assertTrue(res)

        res = self._cache.get('key2')
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()
