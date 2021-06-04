import unittest
from unittest.mock import Mock

from dotenv import load_dotenv

from xcube_hub import api
from xcube_hub.geoservice import GeoService


class TestGeoServiceCore(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')
        self._geoservice = GeoService.instance(provider='geoserver')
        self._geoservice._provider._geo = Mock()

    def test_get_layers(self):
        # Test whether call succeeds
        self._geoservice._provider._geo.get_layers.return_value = {'layers': {'layer': [{'name': 'test'}]}}

        res = self._geoservice.get_layers(database_id='test')
        self.assertDictEqual({'layers': {'layer': [{'name': 'test'}]}}, res)

        def side_effect(workspace):
            raise Exception("Error: test")

        # Test whether method raises
        self._geoservice._provider._geo.get_layers = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.get_layers(database_id='test')

        self.assertEqual('Error: test', str(e.exception))

    def test_get_layer(self):
        # Test whether call succeeds
        self._geoservice._provider._geo.get_layers.return_value = {'layer': {'name': 'test'}}

        res = self._geoservice.get_layer(database_id='test', collection_id='test')

        self.assertDictEqual({'layer': {'name': 'test'}}, res)

        def side_effect(layer_name, workspace):
            raise Exception("Error: test")

        # Test whether method raises
        self._geoservice._provider._geo.get_layer = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.get_layer(database_id='test', collection_id='test')

        self.assertEqual('Error: test', str(e.exception))

    # noinspection PyUnresolvedReferences
    def test_publish(self):
        # Test whether call succeeds if workspace exists
        self._geoservice._provider._geo.get_workspace.return_value = "test"

        res = self._geoservice.publish(database_id='test', collection_id='test')

        self._geoservice._provider._geo.create_workspace.assert_not_called()
        self._geoservice._provider._geo.create_featurestore.assert_not_called()
        self._geoservice._provider._geo.publish_featurestore.assert_called()

        # Test whether call succeeds when workspace has to be created
        self._geoservice._provider._geo.get_workspace.return_value = None

        res = self._geoservice.publish(database_id='test', collection_id='test')

        self._geoservice._provider._geo.create_workspace.assert_called_once()
        self._geoservice._provider._geo.create_featurestore.assert_called_once()
        self._geoservice._provider._geo.publish_featurestore.assert_called()

        def side_effect(workspace, store_name, pg_table):
            raise Exception("Error: test")

        self._geoservice._provider._geo.publish_featurestore = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.publish(database_id='test', collection_id='test')

        self.assertEqual("Error: test", str(e.exception))


if __name__ == '__main__':
    unittest.main()
