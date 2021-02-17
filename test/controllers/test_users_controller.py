# coding: utf-8

from __future__ import absolute_import

import datetime

import requests_mock
from flask import json
from jose import jwt

from xcube_hub.models.user import User
from test import BaseTestCase
from xcube_hub.models.user_app_metadata import UserAppMetadata
from xcube_hub.models.user_user_metadata import UserUserMetadata

AUTH0_DOMAIN = 'edc.eu.auth0.com'
ALGORITHMS = ["RS256"]
DEFAULT_API_IDENTIFIER = 'https://xcube-gen.brockmann-consult.de/api/v2/'
API_AUTH_IDENTIFIER = 'https://edc.eu.auth0.com/api/v2/'


def _generate_token():
    claims = {
        "iss": "https://testiss/",
        "aud": 'https://test',
        "scope": ["manage:users", ],
        "gty": "client-credentials",
        "email": "bla@gmail.com",
        "permissions": ["manage:users", ]
    }

    return jwt.encode(claims, "lkvnsdfvnsdfövndsfvnsdfvndsvnsdflvndf", algorithm="HS256")


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def setUp(self):
        self._token = _generate_token()
        self._user = User(
            user_id='auth0|kalleblomquist',
            email='kalleblomquist@gmail.com',
            username='kalleblomquist',
            nickname='kalle',
            given_name='Kalle',
            family_name='Blomquist',
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            user_metadata=UserUserMetadata(client_id='abc', client_secret='def', punits=1000),
            app_metadata=UserAppMetadata(geodb_role='role'),
            connection="Init",
        )

    @requests_mock.Mocker()
    def test_add_user(self, m):
        """Test case for add_user

        Add user
        """
        m.post(f'https://edc.eu.auth0.com/api/v2/roles/rol_UV2cTM5brIezM6i6/users', json={})
        body = self._user
        m.post("https://edc.eu.auth0.com/oauth/token", json={'access_token': 'sdfvdfv'})
        m.post(f"https://edc.eu.auth0.com/api/v2/users", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            method='PUT',
            json=body.to_dict(),
            headers={'Authorization': f"Bearer {self._token}"},
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.post(f"https://edc.eu.auth0.com/api/v2/users", json=body.to_dict(), status_code=400)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            method='PUT',
            json=body.to_dict(),
            headers={'Authorization': f"Bearer {self._token}"},
            content_type='application/json')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_delete_user_by_user_id(self, m):
        """Test case for delete_user_by_user_id

        Delete user
        """
        body = self._user
        m.delete(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        m.delete(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", status_code=404)

        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE')
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        m.delete(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=500)

        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_get_user_by_user_id(self, m):
        """Test case for get_user_by_user_id

        Get users
        """

        body = self._user
        user_id = 'user_id_example'
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=404)

        response = self.client.open(
            f'/api/v2/users/{user_id}',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=500)

        response = self.client.open(
            f'/api/v2/users/{user_id}',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_get_users(self, m):
        """Test case for get_users

        Get all users by service name
        """

        m.get(f'https://edc.eu.auth0.com/api/v2/users', json=[self._user.to_dict(), ], status_code=200)
        response = self.client.open(
            '/api/v2/users',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.get(f'https://edc.eu.auth0.com/api/v2/users', json=[], status_code=200)
        response = self.client.open(
            '/api/v2/users',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert404(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.get(f'https://edc.eu.auth0.com/api/v2/users', json=[], status_code=500)
        response = self.client.open(
            '/api/v2/users',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_update_user_by_user_id(self, m):
        """Test case for update_user_by_user_id

        Update user
        """
        body = self._user
        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=404)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert404(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=500)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_update_secrets_by_user_id(self, m):
        body = self._user
        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=404)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert404(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=500)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_delete_secrets_by_user_id(self, m):
        body = self._user
        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=404)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert404(response, 'Response body is : ' + response.data.decode('utf-8'))

        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(),
                status_code=500)
        response = self.client.open(
            '/api/v2/users/{user_id}/secrets'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
