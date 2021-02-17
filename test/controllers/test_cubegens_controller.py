# coding: utf-8

from __future__ import absolute_import

from flask import json
from xcube_hub.models.cost_config import CostConfig
from test import BaseTestCase
from xcube_hub.models.cubegen_config import CubegenConfig


class TestCubeGensController(BaseTestCase):
    """CubeGensController integration test stubs"""
    def setUp(self) -> None:
        self._cubegen_id = "dfsvdsfvdv"

    def test_create_cubegen(self):
        """Test case for create_cubegen

        Create a cubegen
        """
        body = CubegenConfig()
        response = self.client.open(
            '/api/v2/cubegens',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegen(self):
        """Test case for delete_cubegen

        Delete a cubegen
        """
        response = self.client.open(f'/api/v2/cubegens/{self._cubegen_id}', method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_cubegens(self):
        """Test case for delete_cubegens

        Delete all cubegens
        """
        response = self.client.open('/api/v2/cubegens', method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_get_costs(self):
        """Test case for get_costs

        Receive cost information for running a cubegen
        """
        body = CostConfig()
        response = self.client.open(
            '/api/v2/cubegens/costs',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegen(self):
        """Test case for get_cubegen

        List specific cubegen
        """
        response = self.client.open(f'/api/v2/cubegens/{self._cubegen_id}', method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_cubegens(self):
        """Test case for get_cubegens

        List cubegens
        """
        response = self.client.open('/api/v2/cubegens', method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
