import json
import unittest

import os
from unittest.mock import patch

from xcube_gen import api
from xcube_gen.cache import Cache


class TestKv(unittest.TestCase):
    def test_instance(self):
        inst = Cache.instance('json')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.kv.JsonKv'>")

        inst = Cache.instance('leveldb', name='/tmp/testinstance')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.kv.LevelDBKv'>")

        inst = Cache.instance('redis')
        self.assertEqual(str(type(inst)), "<class 'xcube_gen.kv.RedisKv'>")

        with self.assertRaises(api.ApiError) as e:
            Cache.instance('jso')

        self.assertEqual("Provider jso not known.", str(e.exception))


class TestRedisKv(unittest.TestCase):
    def setUp(self) -> None:
        self._mock_set_patch = patch('redis.Redis.set')
        self._mock_set = self._mock_set_patch.start()
        self._mock_set.return_value = True

        self._mock_get_patch = patch('redis.Redis.get')
        self._mock_get = self._mock_get_patch.start()

        self._mock_delete_patch = patch('redis.Redis.delete')
        self._mock_delete = self._mock_delete_patch.start()
        self._mock_delete.return_value = True

    def tearDown(self) -> None:
        self._mock_set_patch.stop()
        self._mock_get_patch.stop()
        self._mock_delete_patch.stop()

    def test_get(self):
        self._mock_get.return_value = None

        db = Cache.instance('redis')
        res = db.get('äpasokväp')
        self.assertFalse(res)

        self._mock_get.return_value = 'value'
        res = db.get('key')
        self.assertEqual('value', res)

    def test_set(self):
        self._mock_set.return_value = True

        db = Cache.instance('redis')
        res = db.set('testSet', 'testValue')
        self.assertTrue(res)

        self._mock_get.return_value = 'testValue'
        res = db.get('testSet')
        self.assertEqual('testValue', res)

    def test_delete(self):
        self._mock_delete.return_value = True
        db = Cache.instance('redis')
        res = db.delete('key')
        self.assertTrue(res)

        self._mock_get.return_value = None
        res = db.get('key')
        self.assertFalse(res)


class TestLevelDbKv(unittest.TestCase):
    def setUp(self) -> None:
        self._db = Cache.instance(cache_provider='leveldb', name='/tmp/testleveldb', create_if_missing=True)
        self._db.set('key', 'value')

    def test_get(self):
        res = self._db.get('äpasokväp')
        self.assertFalse(res)

        res = self._db.get('key')
        self.assertEqual('value', res)

    def test_set(self):
        res = self._db.set('testSet', 'testValue')
        self.assertTrue(res)

        res = self._db.get('testSet')
        self.assertEqual('testValue', res)

    def test_delete(self):
        res = self._db.delete('key')
        self.assertTrue(res)

        res = self._db.get('key')
        self.assertFalse(res)


class TestJsonKv(unittest.TestCase):
    def setUp(self) -> None:
        self._json_file = 'callbacks_test.json'
        with open(self._json_file, 'w+') as js:
            json.dump({'key': 'value', 'key2': 'value2'}, js)
            js.close()

        self._db = Cache.instance('json', file_name=self._json_file)

    def tearDown(self) -> None:
        os.unlink(self._json_file)

    def test_get(self):
        res = self._db.get('äpasokväp')
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
