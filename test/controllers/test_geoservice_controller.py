import unittest
from unittest.mock import Mock

import requests_mock
from dotenv import load_dotenv

from test import BaseTestCase
from test.controllers.utils import create_test_token, del_env
from xcube_hub import api
from xcube_hub.geoservice import GeoService
from xcube_hub.models.collection import Collection


@requests_mock.Mocker()
class TestGeoServerController(BaseTestCase):
    def setUp(self):
        load_dotenv(dotenv_path='test/.env')
        self._geo = GeoService.instance(provider='mock')

        self._claims, self._token = create_test_token(permissions=["manage:collections", ], dbrole='geodb_admin')
        self._headers = {'Authorization': f'Bearer {self._token}'}

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')

    def access_mock(self, m):
        res = [{'src': [{'id': 369, 'name': 'terrestris', 'owner': 'geodb_admin', 'iss': None}]}]

        m.post(url='https://stage.xcube-geodb.brockmann-consult.de/rpc/geodb_list_databases',
               headers={'Authorization': f'Bearer {self._token}'}, json=res)

    def test_get_collections(self, m):
        self.access_mock(m)

        # Test whether the controller works
        self._geo._provider = Mock()
        self._geo._provider.get_layers.return_value = {'layers': {'layer': [{'name': 'test'}]}}
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections',
                                    headers=self._headers, method='GET')

        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual(1, len(response.json['layers']['layer']))

        tt = []
        tt.append({'src': None})

        m.post("https://stage.xcube-geodb.brockmann-consult.de/rpc/geodb_list_databases", json=tt)

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections',
                                    headers=self._headers, method='GET')

        self.assert404(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller authorizes

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections', method='GET')

        self.assert401(response, 'Response body is : ' + response.data.decode('utf-8'))

        self.access_mock(m)
        # Test whether the controller returns an error when the service raises an exception
        def side_effect(database_id, fmt):
            raise api.ApiError(400, 'test')

        self._geo._provider.get_layers = side_effect
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections',
                                    headers=self._headers, method='GET')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("test", response.json['message'])

    def test_get_collection(self, m):
        self.access_mock(m)

        # test whether controller works
        self._geo._provider = Mock()
        self._geo._provider.get_layer.return_value = Collection(name='test')

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test',
                                    headers=self._headers, method='GET')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual('test', response.json['name'])

        # Test whether the controller authorizes

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test', method='GET')

        self.assert401(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller returns an error when the service raises an exception
        def side_effect(database_id, collection_id):
            raise api.ApiError(400, 'test')

        self._geo._provider.get_layer = side_effect
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test',
                                    headers=self._headers, method='GET')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("test", response.json['message'])

    def test_put_collection(self, m):
        self.access_mock(m)

        # test whether controller works
        self._geo._provider = Mock()
        self._geo._provider.publish.return_value = Collection(name='test')

        payload = {
            'collection_id': 'anja_E1'
        }
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections',
                                    headers=self._headers, json=payload, method='PUT')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller authorizes

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections', json=payload,
                                    method='PUT')

        self.assert401(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller returns an error when the service raises an exception
        def side_effect(database_id, collection_id):
            raise api.ApiError(400, 'test')

        self._geo._provider.publish = side_effect
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections', json=payload,
                                    headers=self._headers, method='PUT')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("test", response.json['message'])

        # Test whether controller returns an error when collection_id is not in body
        payload = {
            'collection': 'anja_E1'
        }
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections',
                                    headers=self._headers, json=payload, method='PUT')
        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))

        self.assertEqual("put_collection needs a collection_id", response.json['message'])

    def test_delete_collection(self, m):
        self.access_mock(m)

        # test whether controller works
        self._geo._provider = Mock()
        self._geo._provider.unpublish.return_value = Collection(name='test')

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test',
                                    headers=self._headers, method='DELETE')
        self.assert200(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller authorizes

        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test',
                                    method='DELETE')

        self.assert401(response, 'Response body is : ' + response.data.decode('utf-8'))

        # Test whether the controller returns an error when the service raises an exception
        def side_effect(database_id, collection_id):
            raise api.ApiError(400, 'test')

        self._geo._provider.unpublish = side_effect
        response = self.client.open('/api/v2/services/xcube_geoserv/databases/terrestris/collections/test',
                                    headers=self._headers, method='DELETE')

        self.assert400(response, 'Response body is : ' + response.data.decode('utf-8'))
        self.assertEqual("test", response.json['message'])


if __name__ == '__main__':
    unittest.main()
