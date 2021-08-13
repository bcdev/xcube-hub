import unittest
from unittest.mock import Mock

import requests_mock
from dotenv import load_dotenv

from test.controllers.utils import del_env
from xcube_hub import api
# noinspection PyProtectedMember
from xcube_hub.geoservice import GeoService, _GeoServer
from xcube_hub.models.collection import Collection

_FTYPE = {
    "featureType": {
        "name": "test",
        "nativeName": "test",
        "namespace": {
            "name": "db",
            "href": "https://test/geoserver/rest/namespaces/db.json"
        },
        "title": "Test",
        "srs": "EPSG:900913",
        "nativeBoundingBox": {
            "minx": -20037508.3428,
            "maxx": 20037508.3428,
            "miny": -25819498.5135,
            "maxy": 25819498.5135,
            "crs": {
                "@class": "projected",
                "$": "EPSG:900913"
            }
        },
        "latLonBoundingBox": {
            "minx": -180,
            "maxx": 180,
            "miny": -88,
            "maxy": 88,
            "crs": "EPSG:4326"
        }
    }
}

_LAYER = {
    # 'collection_id': 'db_test',
    # 'name': 'test',
    # 'database': 'db',
    # 'wms_uri': 'https://test/hhh',
    'layer': {
        'name': 'test',
        'type': 'WMS',
        'defaultStyle': {
            'name': '',
            'href': 'https://test/geoserver/rest/styles/default.json'
        },
        'resource': {
            '@class': 'wmsLayer',
            'name': 'db:test',
            'href': 'https://test/geoserver/rest/workspaces/db/wmsstores/db-test/wmslayers/test.json'
        },
        'attribution': {
            'logoWidth': 0,
            'logoHeight': 0
        }
    }
}

_EXPECTED_LAYER = {
    'collection_id': 'test',
    'database': 'test',
    'default_style': None,
    'geojson_url': 'https://test/geoserver/drwho/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=drwho:test_test&maxFeatures=10&outputFormat=application/json',
    'href': None,
    'name': 'test',
    'preview_url': 'https://test/geoserver/drwho/wms?service=WMS&version=1.1.0&request=GetMap&layers=drwho:test_test&bbox=-20037508.3428,-25819498.5135,20037508.3428,25819498.5135&width=690&height=768&srs=EPSG:900913&styles=&format=application/openlayers',
    'wfs_url': 'https://test/geoserver/drwho/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=drwho%3Atest_test&maxFeatures=10&outputFormat=application%2Fvnd.google-earth.kml%2Bxml'
}


_EXPECTED_LAYER_GPD_FORMAT = {
    'collection_id': ['test'],
    'database': ['test'],
    'default_style': [None],
    'geojson_url': ['https://test/geoserver/drwho/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=drwho:test_test&maxFeatures=10&outputFormat=application/json'],
    'href': [None],
    'name': ['test'],
    'preview_url': ['https://test/geoserver/drwho/wms?service=WMS&version=1.1.0&request=GetMap&layers=drwho:test_test&bbox=-20037508.3428,-25819498.5135,20037508.3428,25819498.5135&width=690&height=768&srs=EPSG:900913&styles=&format=application/openlayers'],
    'wfs_url': ['https://test/geoserver/drwho/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=drwho%3Atest_test&maxFeatures=10&outputFormat=application%2Fvnd.google-earth.kml%2Bxml']
}


class TestGeoService(unittest.TestCase):
    def test_geoservice_geoserver(self):
        load_dotenv(dotenv_path='test/.env')
        geo = GeoService.instance(provider='geoserver')
        self.assertIsInstance(geo._provider, _GeoServer)
        del_env(dotenv_path='test/.env')

    def test_geoservice_refresh(self):
        # test refresh
        load_dotenv(dotenv_path='test/.env')
        geo = GeoService.instance(provider='geoserver',
                                  url="https://test/geoserver",
                                  username="drwho",
                                  password="timelord",
                                  pg_user='user',
                                  pg_host='https://test',
                                  pg_password='bla',
                                  refresh=True)

        geo = GeoService.instance(provider='geoserver',
                                  url="https://test/geoserver",
                                  username="drwho2",
                                  password="timelord",
                                  pg_user='user',
                                  pg_host='https://test',
                                  pg_password='bla')

        self.assertIsInstance(geo, GeoService)
        self.assertEqual('drwho', geo._provider._username)

        geo = GeoService.instance(provider='geoserver',
                                  url="https://test/geoserver",
                                  username="drwho2",
                                  password="timelord",
                                  pg_user='user',
                                  pg_host='https://test',
                                  pg_password='bla',
                                  refresh=True)

        self.assertIsInstance(geo, GeoService)
        self.assertEqual('drwho2', geo._provider._username)

    def test_geoservice_provider_unknown(self):
        with self.assertRaises(api.ApiError) as e:
            # noinspection PyTypeChecker
            GeoService(provider=None)
        self.assertEqual("Provider None unknown.", str(e.exception))

    def test_geoservice(self):
        GeoService.instance(url='https://test0/geoserver', username='drwho', password='pass', pg_user='pg',
                            pg_password='pwd', pg_host='host', provider='geoserver', refresh=True)
        geo = GeoService.instance(provider='geoserver', pg_user='user', pg_host='https://test', pg_password='bla')

        self.assertIsInstance(geo, GeoService)
        self.assertEqual('https://test0/geoserver', geo._provider._url)
        self.assertEqual('drwho', geo._provider._username)
        self.assertEqual('pass', geo._provider._password)

        geo = GeoService.instance(provider='geoserver',
                                  url="https://test2",
                                  username="drwho",
                                  password="timelord",
                                  pg_user='user',
                                  pg_host='https://test',
                                  pg_password='bla',
                                  refresh=True)

        self.assertIsInstance(geo, GeoService)
        self.assertEqual('https://test2', geo._provider._url)
        self.assertEqual('drwho', geo._provider._username)
        self.assertEqual('timelord', geo._provider._password)


class TestGeoServiceOps(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')
        self._geoservice = GeoService.instance(provider='geoserver')
        self._geoservice._provider._geo = Mock()

    @requests_mock.Mocker()
    def test_get_layers(self, m):
        self.maxDiff = None
        # Test whether call succeeds
        self._geoservice._provider._geo.get_layers.return_value = {'layers': {'layer': [{'name': 'test_test'}]}}
        self._geoservice._provider._geo.get_layer.return_value = {'layer': {'name': 'test_test', 'resource':
            {'href': 'https://test/geoserver'}}}

        m.get('https://test/geoserver', json=_FTYPE)

        res = self._geoservice.get_layers(user_id='drwho', database_id='test', fmt='json')
        self.assertDictEqual(_EXPECTED_LAYER, res[0])

        res = self._geoservice.get_layers(user_id='drwho', database_id='test', fmt='geopandas')
        self.assertDictEqual(_EXPECTED_LAYER_GPD_FORMAT, res)

        def side_effect(workspace):
            raise Exception("Error: test")

        # Test whether method raises
        self._geoservice._provider._geo.get_layers = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.get_layers(user_id='drwho', database_id='test', fmt='json')

        self.assertEqual('Error: test', str(e.exception))

    @requests_mock.Mocker()
    def test_get_layer(self, m):
        # Test whether call succeeds
        m.get('https://test', json=_FTYPE)
        self._geoservice._provider._geo.get_layer.return_value = {'layer': {
            'name': 'drwho', 'resource': {'href': 'https://test'}}
        }

        res = self._geoservice.get_layer(user_id='drwho', database_id='test', collection_id='test')

        self.assertIsInstance(res, Collection)
        self.maxDiff = None
        self.assertDictEqual(_EXPECTED_LAYER, res.to_dict())

        # Test whether method raises
        self._geoservice._provider._geo.get_layer.return_value = 'get_layer error: bla'

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.get_layer(user_id='drwho', database_id='test', collection_id='test')

        self.assertEqual('get_layer error: bla', str(e.exception))

        def side_effect(layer_name, workspace):
            raise Exception("Error: test")

        # Test whether method raises
        self._geoservice._provider._geo.get_layer = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.get_layer(user_id='drwho', database_id='test', collection_id='test')

        self.assertEqual('Error: test', str(e.exception))

    # noinspection PyUnresolvedReferences
    @requests_mock.Mocker()
    def test_publish(self, m):
        m.get('https://test', json=_FTYPE)
        # Test whether call succeeds if workspace exists
        self._geoservice._provider._geo.get_workspace.return_value = "db"
        self._geoservice._provider._geo.get_layer.return_value = {'layer': {
            'name': 'test', 'resource': {'href': 'https://test'}}
        }

        self._geoservice._provider._geo.get_featurestore.return_value = ''
        self._geoservice._provider._geo.publish_featurestore.return_value = None
        res = self._geoservice.publish(user_id='drwho', database_id='test', collection_id='test')
        self.assertDictEqual(_EXPECTED_LAYER, res.to_dict())

        self._geoservice._provider._geo.create_workspace.assert_not_called()
        self._geoservice._provider._geo.create_featurestore.assert_not_called()
        self._geoservice._provider._geo.publish_featurestore.assert_called()

        # Test whether call succeeds when workspace has to be created
        self._geoservice._provider._geo.get_workspace.return_value = None

        res = self._geoservice.publish(user_id='drwho', database_id='test', collection_id='test')

        self._geoservice._provider._geo.create_workspace.assert_called_once()
        self._geoservice._provider._geo.publish_featurestore.assert_called()

        def side_effect(workspace, store_name, pg_table):
            raise Exception("Error: test")

        self._geoservice._provider._geo.publish_featurestore = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.publish(user_id='drwho', database_id='test', collection_id='test')

        self.assertEqual("Error: test", str(e.exception))

    @requests_mock.Mocker()
    def test_unpublish(self, m):
        m.get('https://test', json=_FTYPE)
        # Test whether call succeeds if workspace exists
        self._geoservice._provider._geo.get_workspace.return_value = "db"
        self._geoservice._provider._geo.get_layer.return_value = {'layer': {
            'name': 'test', 'resource': {'href': 'https://test'}}
        }
        self._geoservice._provider._geo.delete_layer.return_value = 'bla'

        res = self._geoservice.unpublish(user_id='drwho', database_id='test', collection_id='test')
        self.assertDictEqual(_EXPECTED_LAYER, res.to_dict())

        def side_effect(workspace, layer_name):
            raise Exception("Error: test")

        self._geoservice._provider._geo.delete_layer = side_effect

        with self.assertRaises(api.ApiError) as e:
            self._geoservice.unpublish(user_id='drwho', database_id='test', collection_id='test')

        self.assertEqual("Error: test", str(e.exception))


if __name__ == '__main__':
    unittest.main()
