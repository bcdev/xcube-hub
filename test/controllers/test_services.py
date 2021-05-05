import unittest

from dotenv import load_dotenv

from test import BaseTestCase
from test.controllers.utils import create_test_token

_SERVICES = ["xcube_gen", "cate"]


class TestServices(BaseTestCase):
    def setUp(self):
        self._claims, self._token = create_test_token(permissions=["manage:subscriptions", ])
        self._headers = {'Authorization': f'Bearer {self._token}'}
        load_dotenv(dotenv_path='test/.env')

    def test_get_services(self):
        response = self.client.open('/api/v2/services', headers=self._headers, method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(_SERVICES, response.json[0])

        response = self.client.open('/api/v2/services', method='GET')
        self.assert401(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
