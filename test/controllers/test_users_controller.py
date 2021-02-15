# coding: utf-8

from __future__ import absolute_import

import os

import requests_mock
from flask import json
from xcube_hub import auth0
from xcube_hub.models.user import User  # noqa: E501
from test import BaseTestCase

AUTH0_DOMAIN = 'edc.eu.auth0.com'
ALGORITHMS = ["RS256"]
DEFAULT_API_IDENTIFIER = 'https://xcube-gen.brockmann-consult.de/api/v2/'
API_AUTH_IDENTIFIER = 'https://edc.eu.auth0.com/api/v2/'


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def setUp(self) -> None:
        os.environ['AUTH0_USER_MANAGEMENT_CLIENT_ID'] = ''
        os.environ[
            'AUTH0_USER_MANAGEMENT_CLIENT_SECRET'] = ''
        self._token = auth0.get_management_token()

    @requests_mock.Mocker()
    def test_add_user(self, m):
        """Test case for add_user

        Add user
        """

        body = User()
        m.post(f"https://edc.eu.auth0.com/api/v2/users", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            method='PUT',
            data=json.dumps(body),
            headers={'Authorization': f"Bearer {self._token}"},
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_delete_user_by_user_id(self, m):
        """Test case for delete_user_by_user_id

        Delete user
        """
        body = User()
        m.delete(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_get_user_by_user_id(self, m):
        """Test case for get_user_by_user_id

        Get users
        """

        body = User()
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)

        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_get_users(self, m):
        """Test case for get_users

        Get all users by service name
        """

        m.get(f'https://edc.eu.auth0.com/api/v2/users', json=[], status_code=200)
        response = self.client.open(
            '/api/v2/users',
            headers={'Authorization': f"Bearer {self._token}"},
            method='GET')
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @requests_mock.Mocker()
    def test_update_user_by_user_id(self, m):
        """Test case for update_user_by_user_id

        Update user
        """
        body = User()
        m.patch(f"https://edc.eu.auth0.com/api/v2/users/user_id_example", json=body.to_dict(), status_code=200)
        m.get(f'https://edc.eu.auth0.com/api/v2/users/user_id_example', json=body.to_dict(), status_code=200)
        response = self.client.open(
            '/api/v2/users/{user_id}'.format(user_id='user_id_example'),
            headers={'Authorization': f"Bearer {self._token}"},
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest

    unittest.main()
