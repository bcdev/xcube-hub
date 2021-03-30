import os
import unittest

from xcube_hub import api
from xcube_hub.core.stores import get_stores_from_file

TEST_POOLS = {'sentinelhub_codede': {'title': 'SENTINEL Hub (Central Europe)', 'store_id': 'sentinelhub',
                                     'cost_params': {'scheme': 'punits', 'input_pixels_per_punit': 262144,
                                                     'input_punits_weight': 1.0, 'output_pixels_per_punit': 262144,
                                                     'output_punits_weight': 1.0},
                                     'store_params': {'api_url': 'https://services.sentinel-hub.com'}}}


class TestStores(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = 'test/resources/data-pools.yaml'

    def test_get_stores(self):
        res = get_stores_from_file()
        self.assertDictEqual(TEST_POOLS, res)

        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = "fff"
        with self.assertRaises(api.ApiError) as e:
            get_stores_from_file()

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual("[Errno 2] No such file or directory: 'fff'", str(e.exception))

        del os.environ['XCUBE_GEN_DATA_POOLS_PATH']
        with self.assertRaises(api.ApiError) as e:
            get_stores_from_file()

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual("Environment Variable XCUBE_GEN_DATA_POOLS_PATH does not exist.", str(e.exception))


if __name__ == '__main__':
    unittest.main()
