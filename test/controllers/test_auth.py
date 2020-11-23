import unittest
import requests_mock
from xcube_hub import api
from xcube_hub.auth0 import AUTH0_DOMAIN
from xcube_hub.controllers import auth


class TestGeodb(unittest.TestCase):
    def setUp(self) -> None:
        self._payload = {
            "email": "john.doe@mail.org",
            "user_metadata": {},
            "blocked": False,
            "email_verified": True,
            "app_metadata": {
                "geodb_role": "geodb_thisismyid"
            },
            "given_name": "John",
            "family_name": "Doe",
            "name": "John Doe",
            "nickname": "thisismyid",
            "username": "geodb_thisismyid",
            "user_id": "thisismyid",
            "connection": "Username-Password-Authentication",
            "password": "thisismysecret",
            "verify_email": False,
        }

    @requests_mock.Mocker()
    def test_register_user(self, m):
        mock_token = "fdvkdfv"

        with self.assertRaises(api.ApiError) as e:
            # noinspection PyTypeChecker
            auth.register_user(token=mock_token, payload=None)

        self.assertEqual("Payload needs to be a dict.", str(e.exception))

        with self.assertRaises(api.ApiError) as e:
            pl = self._payload.copy()
            del pl['user_id']
            auth.register_user(token=mock_token, payload=pl)

        self.assertEqual("Registering a user needs a user_id", str(e.exception))

        with self.assertRaises(api.ApiError) as e:
            pl = self._payload.copy()
            del pl['email']
            auth.register_user(token=mock_token, payload=pl)

        self.assertEqual("Registering a user needs an email", str(e.exception))

        m.post(f"https://{AUTH0_DOMAIN}/api/v2/users", text='test', status_code=400)
        with self.assertRaises(api.ApiError) as e:
            auth.register_user(token=mock_token, payload=self._payload)

        self.assertEqual(f"400 Client Error: None for url: https://{AUTH0_DOMAIN}/api/v2/users", str(e.exception))

        m.post(f"https://{AUTH0_DOMAIN}/api/v2/users", text='test')
        res = auth.register_user(token='ascd', payload=self._payload)
        self.assertEqual(True, res)

    @requests_mock.Mocker()
    def test_delete_user(self, m):
        m.delete(f"https://{AUTH0_DOMAIN}/api/v2/users/asdc", text='test', status_code=400)
        with self.assertRaises(api.ApiError) as e:
            auth.delete_user(token='ascd', user_id='asdc')

        self.assertEqual(f"400 Client Error: None for url: https://{AUTH0_DOMAIN}/api/v2/users/asdc", str(e.exception))

        m.delete(f"https://{AUTH0_DOMAIN}/api/v2/users/asdc", text='test')
        res = auth.delete_user(token='ascd', user_id='asdc')
        self.assertEqual(True, res)

    @requests_mock.Mocker()
    def test_get_user(self, m):
        mock_token = "fdvkdfv"

        with self.assertRaises(api.ApiError) as e:
            pl = self._payload.copy()
            del pl['user_id']
            auth.register_user(token=mock_token, payload=pl)

        self.assertEqual("Registering a user needs a user_id", str(e.exception))

        m.get(f"https://{AUTH0_DOMAIN}/api/v2/users/asdc", json={'email': 'h@mail.org'}, status_code=400)
        with self.assertRaises(api.ApiError) as e:
            auth.get_user(token='ascd', user_id='asdc')

        self.assertEqual(f"400 Client Error: None for url: https://{AUTH0_DOMAIN}/api/v2/users/asdc", str(e.exception))

        m.get(f"https://{AUTH0_DOMAIN}/api/v2/users/asdc", json={'email': 'h@mail.org'})
        res = auth.get_user(token='ascd', user_id='asdc')
        self.assertEqual({'email': 'h@mail.org'}, res)


if __name__ == '__main__':
    unittest.main()
