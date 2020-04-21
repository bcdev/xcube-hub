import unittest

from xcube_gen.controllers.calc import calc_processing_units


class CalcTest(unittest.TestCase):
    def test_calc_processing_units(self):
        result = calc_processing_units({
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
        self.assertEqual({'processingUnits': {'inputCount': 0, 'outputCount': 0, 'totalCount': 0},
                          'sizeEstimation': {'dims': {'time': 365, 'x': 2000, 'y': 2000},
                                             'size': [2000, 2000],
                                             'tileCount': [2, 2],
                                             'tileSize': [1000, 1000],
                                             'variableCount': 3}},
                         result)
