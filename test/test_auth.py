import os
import unittest

from test.setup_utils import setup_auth
from xcube_gen.service import new_app


class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']

    def test_auth0(self):
        res = self._client.get('/')
        self.assertEqual(200, res.status_code, False)


if __name__ == '__main__':
    unittest.main()
