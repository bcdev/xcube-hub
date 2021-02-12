# coding: utf-8

from __future__ import absolute_import

from xcube_hub.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_get_service_info(self):
        """Test case for get_service_info

        get service info
        """
        response = self.client.open(
            '/api/v1/',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
