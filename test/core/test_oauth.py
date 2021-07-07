import unittest

import requests_mock
from dotenv import load_dotenv
from werkzeug.exceptions import Unauthorized

from test.controllers.utils import del_env
from xcube_hub import api
from xcube_hub.core import oauth
from xcube_hub.models.user import User


@requests_mock.Mocker()
class TestOauth(unittest.TestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')

    def test_get_user_by_credentials(self, m):
        user = User(email='drwho@mail.org')
        m.get('https://edc.eu.auth0.com/api/v2/users', json=[user.to_dict()])

        res = oauth.get_user_by_credentials(token='dfasvdsav', client_id='döoasvnoösdvi', client_secret='sdvdsv')

        self.assertEqual(1, len(res))

        m.get('https://edc.eu.auth0.com/api/v2/users', json=[])

        with self.assertRaises(api.ApiError) as e:
            oauth.get_user_by_credentials(token='dfasvdsav', client_id='döoasvnoösdvi', client_secret='sdvdsv')

        self.assertEqual(404, e.exception.status_code)
        self.assertEqual('No users found.', str(e.exception))

        m.get('https://edc.eu.auth0.com/api/v2/users', json=[user.to_dict(), user.to_dict()])

        with self.assertRaises(api.ApiError) as e:
            oauth.get_user_by_credentials(token='dfasvdsav', client_id='döoasvnoösdvi', client_secret='sdvdsv')

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual('More than one user found.', str(e.exception))

        m.get('https://edc.eu.auth0.com/api/v2/users', text='Error', status_code=400)

        with self.assertRaises(api.ApiError) as e:
            oauth.get_user_by_credentials(token='dfasvdsav', client_id='döoasvnoösdvi', client_secret='sdvdsv')

        self.assertEqual('Error', str(e.exception))

    def test_get_token(self, m):
        user = User(email='drwho@mail.org', user_id='drwho', username='drwho', family_name='who', given_name='dr',
                    name='drwho', password='dashc', user_metadata={'client_id': 'snört',
                                                                   'client_secret': 'sdvdsv'},
                    connection='Init',
                    app_metadata={'geodb_role': 'test_role'})
        m.get('https://edc.eu.auth0.com/api/v2/users', json=[user.to_dict()])

        m.post("https://edc.eu.auth0.com/oauth/token", json={'access_token': 'asdcaswdc'})

        m.get(f"https://edc.eu.auth0.com/api/v2/users/drwho/permissions",
              json=[{'permission_name': 'manage:collections'}, ])

        token = {'client_id': 'dfsv', 'client_secret': 'thdrth', 'aud': 'audience', 'grant_type': 'password'}
        res = oauth.get_token(body=token)

        self.assertIn('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9', res)

        token = {'client_id': 'id', 'client_secret': 'sdvdsv', 'aud': 'audience', 'grant_type': 'password'}
        res = oauth.get_token(body=token)

        self.assertEqual('asdcaswdc', res)

        m.post("https://edc.eu.auth0.com/oauth/token", text='error', status_code=401)

        with self.assertRaises(Unauthorized) as e:
            res = oauth.get_token(body=token)

        self.assertEqual('401 Unauthorized: 401 Client Error: None for url: https://edc.eu.auth0.com/oauth/token',
                         str(e.exception))

        m.post("https://edc.eu.auth0.com/oauth/token", json={'access_token_fail': 'asdcaswdc'})

        with self.assertRaises(Unauthorized) as e:
            res = oauth.get_token(body=token)

            self.assertEqual('401 Unauthorized: 401 Client Error: None for url: https://edc.eu.auth0.com/oauth/token',
                             str(e.exception))


if __name__ == '__main__':
    unittest.main()
