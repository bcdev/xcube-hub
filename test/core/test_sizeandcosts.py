import unittest

from xcube_hub import api
from xcube_hub.core import costs
from xcube_hub.models.data_store import DataStore
from xcube_hub.models.data_store_cost_params import DataStoreCostParams
from xcube_hub.models.data_store_store_params import DataStoreStoreParams

_CFG = {
    "dataset_descriptor": {
        "bbox": [
            7.0,
            50.0,
            9.0,
            55.0
        ],
        "crs": "WGS84",
        "data_id": "a02b02a2f186739bff43bb4cd5265ccb8-b28d6f0f-75b0-49c8.zarr",
        "data_vars": {
            "B01": {
                "dims": [
                    "time",
                    "lat",
                    "lon"
                ],
                "dtype": "float32",
                "name": "B01",
                "ndim": 3
            },
            "B02": {
                "dims": [
                    "time",
                    "lat",
                    "lon"
                ],
                "dtype": "float32",
                "name": "B02",
                "ndim": 3
            }
        },
        "dims": {
            "lat": 5000,
            "lon": 2000,
            "time": 14
        },
        "spatial_res": 0.001,
        "time_period": "1D",
        "time_range": [
            "2016-04-17",
            "2016-04-30"
        ],
        "type_specifier": "dataset"
    },
    "size_estimation": {
        "image_size": [
            2000,
            5000
        ],
        "num_bytes": 1120000000,
        "num_requests": 28,
        "num_tiles": [
            1,
            1
        ],
        "num_variables": 2,
        "tile_size": [
            2000,
            5000
        ]
    }
}


_EXP = {'dataset_descriptor': {'bbox': [7.0, 50.0, 9.0, 55.0], 'crs': 'WGS84',
                               'data_id': 'a02b02a2f186739bff43bb4cd5265ccb8-b28d6f0f-75b0-49c8.zarr', 'data_vars': {
        'B01': {'dims': ['time', 'lat', 'lon'], 'dtype': 'float32', 'name': 'B01', 'ndim': 3},
        'B02': {'dims': ['time', 'lat', 'lon'], 'dtype': 'float32', 'name': 'B02', 'ndim': 3}},
                               'dims': {'lat': 5000, 'lon': 2000, 'time': 14}, 'spatial_res': 0.001,
                               'time_period': '1D', 'time_range': ['2016-04-17', '2016-04-30'],
                               'type_specifier': 'dataset'},
        'size_estimation': {'image_size': [2000, 5000], 'num_bytes': 1120000000, 'num_requests': 28,
                            'num_tiles': [1, 1], 'num_variables': 2, 'tile_size': [2000, 5000]},
        'data_store': {'title': 'SENTINEL Hub (CODE-DE)', 'store_id': 'sentinelhub',
                       'cost_params': {'input_pixels_per_punit': 262144, 'input_punits_weight': 1.0,
                                       'output_pixels_per_punit': 262144, 'output_punits_weight': 1.0},
                       'store_params': {'api_url': 'https://code-de.sentinel-hub.com'}},
        'punits': {'input_count': 1092, 'input_weight': 1.0, 'output_count': 1092, 'output_weight': 1.0,
                   'total_count': 1092}}


class TestCosts(unittest.TestCase):
    def setUp(self):
        self._datastore = DataStore(
            title="SENTINEL Hub (CODE-DE)",
            store_id="sentinelhub",
            cost_params=DataStoreCostParams(
                input_pixels_per_punit=262144,
                input_punits_weight=1.0,
                output_pixels_per_punit=262144,
                output_punits_weight=1.0
            ),
            store_params=DataStoreStoreParams(
                api_url="https://code-de.sentinel-hub.com"
            )
        )

    def test_get_size_and_cost(self):
        res = costs.get_size_and_cost(_CFG, self._datastore.to_dict())
        self.assertDictEqual(_EXP, res)

        cfg = {}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('missing request key "dataset_descriptor"', str(e.exception))

        cfg['dataset_descriptor'] = {}
        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('missing request key "data_vars"', str(e.exception))

        cfg['dataset_descriptor']["data_vars"] = {}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('Number of variables must be greater than 0.', str(e.exception))

        cfg['dataset_descriptor']["data_vars"] = {
            'B01': {}
        }

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('missing request key "dims"', str(e.exception))

        cfg['dataset_descriptor']["dims"] = {}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('missing request key "time"', str(e.exception))

        cfg['dataset_descriptor']["dims"]["time"] = 14

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('Cannot find a valid spatial dimension.', str(e.exception))

        cfg['dataset_descriptor']["dims"]["lat"] = 22.6

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('Cannot find a valid spatial dimension.', str(e.exception))

        cfg['dataset_descriptor']["dims"]["lon"] = 22.6

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertEqual('missing request key "size_estimation"', str(e.exception))

        cfg['size_estimation'] = {}

        exp = {'input_count': 14.0, 'input_weight': 1.0, 'output_count': 14.0, 'output_weight': 1.0, 'total_count': 14}
        res = costs.get_size_and_cost(cfg, self._datastore.to_dict())

        self.assertDictEqual(exp, res['punits'])

    def test_get_size_and_cost_datastore(self):
        res = costs.get_size_and_cost(_CFG, self._datastore.to_dict())
        self.assertDictEqual(_EXP, res)

        datastore = DataStore(
            title="SENTINEL Hub (CODE-DE)",
            store_id="sentinelhub",
            cost_params=DataStoreCostParams(
                input_pixels_per_punit=262144,
                input_punits_weight=1.0,
                output_pixels_per_punit=262144,
                output_punits_weight=1.0
            ),
            store_params=DataStoreStoreParams(
                api_url="https://code-de.sentinel-hub.com"
            )
        )

        datastore = {}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('missing request key "cost_params"', str(e.exception))

        datastore = {"cost_params": {}}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('missing request key "input_pixels_per_punit"', str(e.exception))

        datastore = {"cost_params": {"input_pixels_per_punit": 0}}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('Value must be greater than 0', str(e.exception))

        datastore = {"cost_params": {"input_pixels_per_punit": 10}}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('missing request key "input_punits_weight"', str(e.exception))

        datastore = {"cost_params": {"input_pixels_per_punit": 10, "input_punits_weight": 0.0}}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('Value must be greater than 0', str(e.exception))

        datastore = {"cost_params": {"input_pixels_per_punit": 10, "input_punits_weight": 10.0}}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('missing request key "output_pixels_per_punit"', str(e.exception))

        datastore = {"cost_params": {
            "input_pixels_per_punit": 10,
            "input_punits_weight": 10.0,
            "output_pixels_per_punit": 0
        }}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('Value must be greater than 0', str(e.exception))

        datastore = {"cost_params": {
            "input_pixels_per_punit": 10,
            "input_punits_weight": 10.0,
            "output_pixels_per_punit": 10
        }}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('missing request key "output_punits_weight"', str(e.exception))

        datastore = {"cost_params": {
            "input_pixels_per_punit": 10,
            "input_punits_weight": 10.0,
            "output_pixels_per_punit": 10,
            "output_punits_weight": 0.
        }}

        with self.assertRaises(api.ApiError) as e:
            res = costs.get_size_and_cost(_CFG, datastore)

        self.assertEqual('Value must be greater than 0', str(e.exception))


if __name__ == '__main__':
    unittest.main()
