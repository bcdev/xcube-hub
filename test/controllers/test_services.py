import unittest

from dotenv import load_dotenv

from test import BaseTestCase
from test.controllers.utils import create_test_token

_SERVICES = ["xcube_gen", "cate"]


class TestServices(BaseTestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')
        self._claims, self._token = create_test_token(permissions=["manage:services", ])
        self._headers = {'Authorization': f'Bearer {self._token}'}

    def test_get_services(self):
        response = self.client.open('/api/v2/services', method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(_SERVICES, response.json[0])


if __name__ == '__main__':
    unittest.main()
