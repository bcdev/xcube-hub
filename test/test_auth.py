import unittest

from test.setup_auth import setup_auth
from xcube_gen.service import new_app


class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        self._access_token = setup_auth()

        self._app = new_app()
        self._client = self._app.test_client()

    def test_auth0(self):
        res = self._client.get('/', headers={'Authorization': 'Bearer ' + self._access_token['access_token']})
        self.assertEqual(200, res.status_code, False)

        res = self._client.get('/', headers={'Authorization': 'Bearer IDUH DIUHF'})

        self.assertEqual(500, res.status_code)

        res = self._client.get('/')
        self.assertEqual(500, res.status_code)


if __name__ == '__main__':
    unittest.main()
