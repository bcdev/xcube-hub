import json
import unittest
from unittest.mock import patch
from xcube_gen import api
from xcube_gen.keyvaluedatabase import KeyValueDatabase, _LevelDBKvDB, _KvDBMocker, _InMemoryKvDB, _RedisKvDB


class TestKvDB(unittest.TestCase):
    def test_instance(self):
        KeyValueDatabase._instance = None
        inst = KeyValueDatabase.instance(provider='inmemory')
        self.assertEqual(str(type(inst._provider)), "<class 'xcube_gen.keyvaluedatabase._InMemoryKvDB'>")

        KeyValueDatabase._instance = None
        inst = KeyValueDatabase.instance(provider='leveldb', name='/tmp/testinstance')
        self.assertEqual(str(type(inst._provider)), "<class 'xcube_gen.keyvaluedatabase._LevelDBKvDB'>")

        KeyValueDatabase._instance = None
        inst = KeyValueDatabase.instance(provider='redis')
        self.assertEqual(str(type(inst._provider)), "<class 'xcube_gen.keyvaluedatabase._RedisKvDB'>")

        inst = KeyValueDatabase.instance()
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.keyvaluedatabase.KeyValueDatabase'>")

        KeyValueDatabase._instance = None
        with self.assertRaises(api.ApiError) as e:
            KeyValueDatabase.instance('jso')

        self.assertEqual("Provider jso unknown.", str(e.exception))


class TestRedisCache(unittest.TestCase):
    def setUp(self) -> None:
        self._db = _RedisKvDB()

    def test_get(self):
        _mock_patch = patch('redis.Redis.get')
        _mock = _mock_patch.start()

        _mock.return_value = None

        res = self._db.get('äpasoCacheäp')
        self.assertIsNone(res)
        _mock_patch.stop()

        _mock_patch = patch('redis.Redis.get')
        _mock = _mock_patch.start()

        _mock.return_value = {'value': 'testValue'}
        res = self._db.get('key')
        self.assertEqual({'value': 'testValue'}, res)

        _mock_patch.stop()

    def test_set(self):
        _mock_patch = patch('redis.Redis.set')
        _mock = _mock_patch.start()

        _mock.return_value = True

        res = self._db.set('testSet', {'value': 'testValue'})

        self.assertTrue(res)

        _mock_patch.stop()

        _mock_patch = patch('redis.Redis.get')
        _mock = _mock_patch.start()
        _mock.return_value = {'value': 'testValue'}

        res = self._db.get('testSet')

        self.assertEqual({'value': 'testValue'}, res)

    def test_delete(self):
        _mock_patch = patch('redis.Redis.delete')
        _mock = _mock_patch.start()

        _mock.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        _mock_patch.stop()

        _mock_patch = patch('redis.Redis.get')
        _mock = _mock_patch.start()
        _mock.return_value = None
        res = self._db.get('key')
        self.assertFalse(res)

        _mock_patch.stop()


class TestLevelDbCache(unittest.TestCase):
    def setUp(self) -> None:
        self._db = _LevelDBKvDB(name='/tmp/testleveldb', create_if_missing=True, use_mocker=True)

    def test_get(self):
        _KvDBMocker.return_value = None
        res = self._db.get('äpasoCacheäp')
        self.assertIsNone(res)

    def test_gets(self):
        value = json.dumps({'value': 'value'})
        _KvDBMocker.return_value = str.encode(value)
        res = self._db.get('key')
        self.assertEqual(value, res)

    def test_set(self):
        _KvDBMocker.return_value = True
        value = json.dumps({'value': 'value'})
        res = self._db.set('testSet', value)
        self.assertTrue(res)

        _KvDBMocker.return_value = str.encode(value)

        res = self._db.get('testSet')
        self.assertEqual(value, res)

    def test_delete(self):
        _KvDBMocker.return_value = True

        res = self._db.delete('key')
        self.assertTrue(res)

        _KvDBMocker.return_value = None
        res = self._db.get('key')

        self.assertFalse(res)


class TestInMemoryCache(unittest.TestCase):
    def setUp(self) -> None:
        KeyValueDatabase._provider = None
        self._cache = _InMemoryKvDB(db_init={'key': {'value': 'value'}, 'key2': {'value2': 'value2'}})

    def test_get(self):
        res = self._cache.get('äpasoCacheäp')
        self.assertIsNone(res)

        res = self._cache.get('key')
        self.assertEqual(json.dumps({'value': 'value'}), res)

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
