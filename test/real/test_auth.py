import json
import os
import unittest
import uuid
import dotenv

from xcube_hub.controllers import auth
import http.client


def get_auth_token():
    conn = http.client.HTTPSConnection("edc.eu.auth0.com")

    dotenv.load_dotenv(dotenv_path='test/envs/.env', verbose=True)
    client_id = os.environ.get("XCUBE_AUTH_TEST_CLIENT_ID")
    client_secret = os.environ.get("XCUBE_AUTH_TEST_CLIENT_SECRET")

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://edc.eu.auth0.com/api/v2/",
        "grant_type": "client_credentials"
    }

    headers = {
        'content-type': "application/json"
    }

    conn.request("POST", "/oauth/token", json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    res.close()
    data = json.loads(data)
    return data['access_token']


class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        self._user_id = str(uuid.uuid1())
        self._username = f"geodb_{self._user_id[:20]}"
        self._payload = {
            "email": f"ci_{self._user_id}@mail.org",
            "user_metadata": {},
            "blocked": False,
            "email_verified": True,
            "app_metadata": {
                "geodb_role": f"geodb_{self._user_id}"
            },
            "given_name": "John",
            "family_name": "Doe",
            "name": self._username,
            "nickname": "thisismyid",
            "username": f"geodb_{self._user_id[:20]}",
            "user_id": self._user_id,
            "connection": "Username-Password-Authentication",
            "password": self._user_id,
            "verify_email": False,
        }

        self._token = get_auth_token()

    @unittest.skipIf(os.environ.get("SKIP_REAL_HTTP_TESTS", '0') == '1', "REAL HTTP TESTS SKIPPED")
    def test_user(self):
        res = auth.register_user(token=self._token, payload=self._payload)
        self.assertEqual(True, res)

        res = auth.get_user(token=self._token, user_id="auth0|" + self._user_id)
        self.assertEqual(f'ci_{self._user_id}@mail.org', res['email'])

        res = auth.add_user_to_role(token=self._token, user_id="auth0|" + self._user_id, role_id="rol_U7GBF1KSurpxhfTI")
        self.assertEqual({}, res)

        res = auth.delete_user(token=self._token, user_id="auth0|" + self._user_id)
        self.assertEqual(True, res)


if __name__ == '__main__':
    unittest.main()
