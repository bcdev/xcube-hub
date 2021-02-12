import unittest

from xcube_hub_old.api import ApiError
from xcube_hub_old.controllers.sizeandcost import get_size_and_cost


class CalcTest(unittest.TestCase):
    def test_get_size_and_cost_sh(self):
        data = {"input_configs": [
            {
                "store_id": "@sentinelhub",
                "data_id": "S2L2A",
                "open_params": {
                    "tile_size": [
                        1024,
                        1024
                    ]
                }
            }
        ],
            "cube_config": {
                "variable_names": [
                    "B01",
                    "B02"
                ],
                "bbox": [
                    7,
                    53,
                    9,
                    55
                ],
                "spatial_res": 0.001,
                "crs": "WGS84",
                "time_range": [
                    "2020-09-01",
                    "2020-10-20"
                ],
                "time_period": "1H"
            },
            "output_config": {
                "store_id": "s3",
                "store_params": {
                    "bucket_name": "test",
                    "aws_access_key_id": "dasvasdadsv",
                    "aws_secret_access_key": "dfvdsfvdsvdfsv"
                }
            }
        }
        result = get_size_and_cost(data)
        self.assertDictEqual({
            'schema': {
                'dims': {
                    'time': 1177,
                    'y': 2048,
                    'x': 2048
                },
                'image_size': [2048, 2048],
                'tile_size': [1024, 1024],
                'num_variables': 2,
                'num_tiles': [2, 2],
                'num_requests': 9416,
                'num_bytes': 39493566464
            },
            'punits': {
                'input_count': 37664,
                'input_weight': 1.0,
                'output_count': 37664,
                'output_weight': 1.0,
                'total_count': 37664
            }
        }, result)

    def test_get_size_and_cost_cci(self):
        result = get_size_and_cost({
            "input_configs": [
                {
                    "store_id": "@cciodp",
                    "data_id": "esacci.OC.mon.L3S.CHLOR_A.multi-sensor.multi-platform.MERGED.3-1.geographic",
                    "open_params": {}
                }
            ],
            "cube_config": {
                "variable_names": [
                    "chlor_a"
                ],
                "bbox": [
                    7,
                    53,
                    9,
                    55
                ],
                "spatial_res": 0.041666666666666664,
                "crs": "WGS84",
                "time_range": [
                    "1997-09-03",
                    "2016-12-31"
                ],
                "time_period": "5D"
            },
            "output_config": {
                "store_id": "s3",
                "store_params": {
                    "bucket_name": "test",
                    "aws_access_key_id": "dfsvdfsv",
                    "aws_secret_access_key": "dfvdas"
                }
            }
        })
        self.assertDictEqual({
            'schema': {
                'dims': {
                    'time': 1412,
                    'y': 48,
                    'x': 48
                },
                'image_size': [48, 48],
                'tile_size': [1, 1],
                'num_variables': 1,
                'num_tiles': [48, 48],
                'num_requests': 3253248,
                'num_bytes': 13012992
            },
            'punits': {
                'input_count': 1412,
                'input_weight': 1.0,
                'output_count': 1412,
                'output_weight': 1.0,
                'total_count': 1412
            }
        }, result)

    def test_get_size_and_cost_cds(self):
        result = get_size_and_cost({
            "input_configs": [
                {
                    "store_id": "@cds",
                    "data_id": "reanalysis-era5-land",
                    "open_params": {
                        "tile_size": [
                            1024,
                            1024
                        ]
                    }
                }
            ],
            "cube_config": {
                "variable_names": [
                    "2m_temperature"
                ],
                "bbox": [
                    7,
                    53,
                    9,
                    55
                ],
                "spatial_res": 0.1,
                "crs": "WGS84",
                "time_range": [
                    "1981-01-01",
                    "1982-01-01"
                ],
                "time_period": "1H"
            },
            "output_config": {
                "store_id": "s3",
                "store_params": {
                    "bucket_name": "eurodatacube-test",
                    "aws_access_key_id": "AKIAVBLQBN5YKECLN5QL",
                    "aws_secret_access_key": "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"
                }
            }
        })

        self.assertDictEqual({
            'schema': {
                'dims': {
                    'time': 8761,
                    'y': 20,
                    'x': 20
                },
                'image_size': [20, 20],
                'tile_size': [20, 20],
                'num_variables': 1,
                'num_tiles': [1, 1],
                'num_requests': 8761,
                'num_bytes': 14017600
            },
            'punits': {
                'input_count': 8761,
                'input_weight': 1.0,
                'output_count': 8761,
                'output_weight': 1.0,
                'total_count': 8761
            }
        }, result)

    def test_get_size_and_cost_invalid(self):
        with self.assertRaises(ApiError) as cm:
            get_size_and_cost({
                "input_configs": [
                    {
                        "store_id": "@bölablubb",
                        "data_id": "esacci.OC.mon.L3S.CHLOR_A.multi-sensor.multi-platform.MERGED.3-1.geographic",
                        "open_params": {}
                    }
                ],
                "cube_config": {
                    "variable_names": [
                        "chlor_a"
                    ],
                    "bbox": [
                        7,
                        53,
                        9,
                        55
                    ],
                    "spatial_res": 0.041666666666666664,
                    "crs": "WGS84",
                    "time_range": [
                        "1997-09-03",
                        "2016-12-31"
                    ],
                    "time_period": "5D"
                },
                "output_config": {
                    "store_id": "s3",
                    "store_params": {
                        "bucket_name": "test",
                        "aws_access_key_id": "dfsvdfsv",
                        "aws_secret_access_key": "dfvdas"
                    }
                }
            })
        self.assertEqual('unsupported "input_config/datastore_id" entry: "@bölablubb"', f'{cm.exception}')
