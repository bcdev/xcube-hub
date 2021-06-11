import unittest
from unittest.mock import patch

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.controllers import users


class TestUsers(BaseTestCase):
    @patch('xcube_hub.core.cate.launch_cate', create=True)
    def test_put_user_webapi(self, p):
        p.return_value = dict(serverUrl=f'https://test/drwho')

        res = users.put_user_webapi(user_id='drwho')

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = users.put_user_webapi(user_id='drwho')

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cate.get_status', create=True)
    def test_get_user_webapi(self, p):
        p.return_value = dict(serverUrl=f'https://test/drwho')

        res = users.get_user_webapi(user_id='drwho')

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = users.get_user_webapi(user_id='drwho')

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])

    @patch('xcube_hub.core.cate.delete_cate', create=True)
    def test_delete_user_webapi(self, p):
        p.return_value = True

        res = users.delete_user_webapi(user_id='drwho')

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = users.delete_user_webapi(user_id='drwho')

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])


if __name__ == '__main__':
    unittest.main()
