import os
import unittest

from test.controllers.utils import create_test_token
from xcube_hub.core import cubegens

_CFG = {
    "input_config":
        {
            "store_id": "@sentinelhub_codede",
            "data_id": "S3OLCI",
            "open_params": {
                "tile_size": [
                    1024,
                    1024
                ]
            }
        }
    ,
    "cube_config": {
        "variable_names": [
            "B01",
            "B02"
        ],
        "crs": "WGS84",
        "spatial_res": 0.001,
        "bbox": [
            7,
            50,
            9,
            55
        ],
        "time_range": [
            "2016-04-17",
            "2016-04-30"
        ],
        "time_period": "1D"
    }
}


@unittest.skipIf(os.getenv("UNITTESTS_SKIP_K8s", "0") == "1", "Kubernetes skipped")
class TestCubeGens(unittest.TestCase):
    def setUp(self) -> None:
        self._claims, self._token = create_test_token(['manage:cubegens'])
        os.environ["XCUBE_GEN_DATA_POOLS_PATH"] = "test/resources/data-pools.yaml"
        os.environ["XCUBE_HUB_RUN_LOCAL"] = "1"

    def test_info(self):
        res = cubegens.info(user_id='helge', email="helge@mail.com", body=_CFG, token=self._token)
        # self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
