import json
import unittest
from unittest.mock import patch

from xcube_gen import api
from xcube_gen.controllers.callback import get_callback, put_callback, delete_callback


class TestCallback(unittest.TestCase):
    def test_get_callback(self):
        expected = {
            'message': 'bla',
            'status': 'ERROR'
        }

        mock_get_patch = patch('redis.Redis.get')
        mock_get = mock_get_patch.start()
        mock_get.return_value = json.dumps(expected)

        res = get_callback('user2', 'job3')
        self.assertTrue(res)

        mock_get.return_value = None
        with self.assertRaises(api.ApiError) as e:
            get_callback('user2', 'job3')

        self.assertEqual('Could not find any callbacks', str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        mock_get_patch.stop()

    def test_put_callback(self):
        expected = {
            'message': 'bla',
            'status': 'ERROR'
        }

        mock_set_patch = patch('redis.Redis.set')
        mock_set = mock_set_patch.start()
        mock_set.return_value = True

        res = put_callback('user2', 'job3', expected, {})
        self.assertTrue(res)

        mock_set_patch.stop()

    def test_delete_callback(self):
        mock_delete_patch = patch('redis.Redis.delete')
        mock_delete = mock_delete_patch.start()
        mock_delete.return_value = 1

        res = delete_callback('user2', 'job3')
        self.assertEqual(1, res)

        mock_delete.return_value = 0
        with self.assertRaises(api.ApiError) as e:
            delete_callback('user2', 'job3')

        self.assertEqual('Callback not found', str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        mock_delete.return_value = None
        with self.assertRaises(api.ApiError) as e:
            delete_callback('user2', 'job3')

        self.assertEqual('Deletion error', str(e.exception))
        self.assertEqual(401, e.exception.status_code)
        mock_delete_patch.stop()


if __name__ == '__main__':
    unittest.main()
