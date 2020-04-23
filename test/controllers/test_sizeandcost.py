import unittest

from xcube_gen.controllers.sizeandcost import get_size_and_cost


class CalcTest(unittest.TestCase):
    def test_get_size_and_cost(self):
        result = get_size_and_cost({
            "cube_config": {
                "dataset_name": "S2L2A",
                "band_names": [
                    "B01",
                    "B02",
                    "B03"
                ],
                "tile_size": [
                    1000,
                    1000
                ],
                "geometry": [
                    7.0,
                    53.0,
                    9.0,
                    55.0
                ],
                "spatial_res": 0.001,
                "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
                "time_range": [
                    "2019-01-01",
                    "2019-12-31"
                ],
                "time_period": "1D",
                "time_tolerance": "10M"
            },
            "input_config": {
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
