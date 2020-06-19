import json
import unittest
from unittest.mock import patch
import os
from test.setup_utils import setup_auth, set_env
from xcube_gen import api
from xcube_gen.controllers.callback import get_callback, put_callback, delete_callback
from xcube_gen.kvdb import KvDB
from xcube_gen.service import new_app


KvDB.use_mocker = True


class TestCallback(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']
        set_env()

    def test_get_callback(self):
        expected = {
            'message': 'bla',
            'status': 'ERROR'
        }

        mock_get_patch = patch('xcube_gen.kvdb.KvDB.get')
        mock_get = mock_get_patch.start()
        mock_get.return_value = json.dumps(expected)

        res = get_callback('user2', 'job3')
        self.assertTrue(res)

        mock_get.return_value = None
        with self.assertRaises(api.ApiError) as e:
            get_callback('user2', 'job3')

        self.assertEqual('Could not find any callback entries for that key.', str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        mock_get_patch.stop()

    def test_put_callback(self):
        expected = {
            "status": "CUBE_GENERATED",
            "message": "Cube generation finished",
            "values": {
                "punits": {
                    "total_count": 1000
                }
            }
        }

        mock_put_patch = patch('xcube_gen.kvdb.KvDB.get')
        mock_put = mock_put_patch.start()
        mock_put.return_value = True
        mock_put_patch.stop()

        res = put_callback(user_id='ad659004d45088b035f19ec6ff1530b43', job_id='job3', value=expected)
        self.assertTrue(res)

    def test_delete_callback(self):
        mock_delete_patch = patch('xcube_gen.kvdb.KvDB.delete')
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
