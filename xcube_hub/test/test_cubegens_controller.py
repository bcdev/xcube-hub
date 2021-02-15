# coding: utf-8

from __future__ import absolute_import

from flask import json
from xcube_hub.models.cost_config import CostConfig  # noqa: E501
from xcube_hub.models.cubegen_config import CubeGenConfig  # noqa: E501
from xcube_hub.test import BaseTestCase


class TestCubeGensController(BaseTestCase):
    """CubeGensController integration test stubs"""

    def test_create_cubegen(self):
        """Test case for create_cubegen

        Create a cubegen
        """
        body = CubeGenConfig()
        response = self.client.open(
            '/api/v2/cubegens',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegen(self):
        """Test case for delete_cubegen

        Delete a cubegen
        """
        cubegen_id = 'cubegen_id_example'

        response = self.client.open(f'/api/v2/cubegens/{cubegen_id}', method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegens(self):
        """Test case for delete_cubegens

        Delete all cubegens
        """
        response = self.client.open(
            '/api/v2/cubegens',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_costs(self):
        """Test case for get_costs

        Receive cost information for runnning a cubegen
        """
        body = CostConfig()
        response = self.client.open(
            '/api/v2/cubegens/costs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegen(self):
        """Test case for get_cubegen

        List specific cubegen
        """
        response = self.client.open(
            '/api/v2/cubegens/{cubegen_id}'.format(cubegen_id='cubegen_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegens(self):
        """Test case for get_cubegens

        List cubegens
        """
        response = self.client.open(
            '/api/v2/cubegens',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
