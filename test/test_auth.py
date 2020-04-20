import json
import unittest
import http.client

from xcube_gen.service import new_app


class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        conn = http.client.HTTPSConnection("edc.eu.auth0.com")
        payload = "{\"client_id\":\"13eBlDZ6a4pQr5oY9gm26YZ1coRZTs3J\"," \
                  "\"client_secret\":\"iiXKa3zmyMnmj0fyeC_93Gf9bDKe4Pf-Q-D5naljNSfQ7q8t_iLVE9vQinCQZUv5\"," \
                  "\"audience\":\"https://xcube-gen.brockmann-consult.de/api/v1/\"," \
                  "\"grant_type\":\"client_credentials\"}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))
        self._access_token = json.loads(data.decode("utf-8"))

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
