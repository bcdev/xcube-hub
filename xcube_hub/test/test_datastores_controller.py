# coding: utf-8

from __future__ import absolute_import

from xcube_hub.test import BaseTestCase


class TestDatastoresController(BaseTestCase):
    """DatastoresController integration test stubs"""

    def test_get_data_store_by_datastore_id(self):
        """Test case for get_data_store_by_datastore_id

        Get a datastore
        """
        response = self.client.open(
            '/api/v2/datastores/{datastore_id}'.format(datastore_id='datastore_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_data_stores(self):
        """Test case for get_data_stores

        Get a list of datastores
        """
        response = self.client.open(
            '/api/v2/datastores',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
