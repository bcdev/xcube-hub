import os
import unittest

from test.setup_auth import setup_auth
from xcube_gen.service import new_app


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']

    def test_list(self):
        res = self._client.post('/user_namespaces/daffy-duck')
        self.assertEqual('200 OK', res.json['status'])

        res = self._client.get('/user_namespaces/daffy-duck')
        self.assertEqual('ok', res.json['status'])
        self.assertIn('daffy-duck', res.json['result'])

        res = self._client.delete('/user_namespaces/daffy-duck')
        self.assertEqual('200 OK', res.json['status'])


if __name__ == '__main__':
    unittest.main()
