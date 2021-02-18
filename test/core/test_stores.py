import os
import unittest

from xcube_hub import api
from xcube_hub.core.stores import get_stores_from_file

TEST_POOLS = {
    "cds": {
        "title": "C3S Climate Data Store (CDS)",
        "description": "Selected datasets from the Copernicus CDS API",
        "store_id": "cds"
    },
    "cciodp": {
        "title": "ESA Climate Change Initiative (CCI)",
        "description": "Data from the ESA CCI Open Data Portal API",
        "store_id": "cciodp"
    }
}


class TestStores(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = 'test/resources/data-pools.yaml'

    def test_get_stores(self):
        res = get_stores_from_file()
        self.assertDictEqual(TEST_POOLS, res)

        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = 'test/resources/data-pools-invalid.yaml'
        with self.assertRaises(api.ApiError) as e:
            get_stores_from_file()

        self.assertEqual(400, e.exception.status_code)
        self.assertIn("while parsing a block collection", str(e.exception))

        os.environ['XCUBE_GEN_DATA_POOLS_PATH'] = "fff"
        with self.assertRaises(api.ApiError) as e:
            get_stores_from_file()

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual("[Errno 2] No such file or directory: 'fff'", str(e.exception))

        del os.environ['XCUBE_GEN_DATA_POOLS_PATH']
        with self.assertRaises(api.ApiError) as e:
            get_stores_from_file()

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual("Environment Variable XCUBE_GEN_DATA_POOLS_PATH must be given.", str(e.exception))


if __name__ == '__main__':
    unittest.main()
