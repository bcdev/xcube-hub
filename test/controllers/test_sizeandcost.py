import os
import unittest

from test.setup_utils import setup_auth
from xcube_hub.api import ApiError
from xcube_hub.controllers.sizeandcost import get_size_and_cost
from xcube_hub.service import new_app


class CalcTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RUN_LOCAL"] = '1'
        self._access_token = setup_auth()
        self._app = new_app()
        self._client = self._app.test_client()
        self._client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + self._access_token['access_token']

    def test_get_size_and_cost_sh(self):
        result = get_size_and_cost({
            "input_config": {
                "datastore_id": "sentinelhub",
            },
            "cube_config": {
                "dataset_name": "S2L2A",
                "variable_names": ["B01", "B02", "B03"],
                "tile_size": [1000, 1000],
                "geometry": [7.0, 53.0, 9.0, 55.0],
                "spatial_res": 0.001,
                "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
                "time_range": ["2019-01-01", "2019-12-31"],
                "time_period": "1D",
                "time_tolerance": "10M"
            },
            "output_config": {
            }
        })
        self.assertEqual({'punits': {'input_count': 17520,
                                     'input_weight': 1.0,
                                     'output_count': 17520,
                                     'output_weight': 1.0,
                                     'total_count': 17520},
                          'schema': {'dims': {'lat': 2000, 'lon': 2000, 'time': 365},
                                     'num_variables': 3,
                                     'num_requests': 4380,
                                     'num_bytes': 17520000000,
                                     'num_tiles': [2, 2],
                                     'image_size': [2000, 2000],
                                     'tile_size': [1000, 1000]}},
                         result)

    def test_get_size_and_cost_cci(self):
        result = get_size_and_cost({
            "input_config": {
                "datastore_id": "cciodp",
            },
            "cube_config": {
                "dataset_name": "esacci.OZONE.month.L3.NP.multi-sensor.multi-platform.MERGED.fv0002.r1",
                "variable_names": ["O3e_du_tot", "surface_pressure"],
                "geometry": [-180, -90, 180, 90],
                "spatial_res": 0.5,
                "tile_size": [720, 360],
                "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
                "time_range": ["2010-01-01", "2010-12-31"],
                "time_period": "1D",
            },
            "output_config": {
            }
        })
        self.assertEqual({'punits': {'input_count': 730,
                                     'input_weight': 1.0,
                                     'output_count': 730,
                                     'output_weight': 1.0,
                                     'total_count': 730},
                          'schema': {'dims': {'lat': 360, 'lon': 720, 'time': 365},
                                     'image_size': [720, 360],
                                     'num_bytes': 756864000,
                                     'num_requests': 730,
                                     'num_tiles': [1, 1],
                                     'num_variables': 2,
                                     'tile_size': [720, 360]}},
                         result)

    def test_get_size_and_cost_invalid(self):
        with self.assertRaises(ApiError) as cm:
            get_size_and_cost({
                "input_config": {
                    "datastore_id": "c3s",
                },
                "cube_config": {
                    "dataset_name": "esacci.OZONE.month.L3.NP.multi-sensor.multi-platform.MERGED.fv0002.r1",
                    "band_names": ["O3e_du_tot", "surface_pressure"],
                    "geometry": [-180, -90, 180, 90],
                    "spatial_res": 0.5,
                    "tile_size": [720, 360],
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
                    "time_range": ["2010-01-01", "2010-12-31"],
                    "time_period": "1D",
                },
                "output_config": {
                }
            })
        self.assertEqual('unsupported "input_config/datastore_id" entry: "c3s"', f'{cm.exception}')