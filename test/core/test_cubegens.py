import unittest
from unittest.mock import patch

from dotenv import load_dotenv
from kubernetes.client import ApiException, BatchV1Api, V1Pod, V1ObjectMeta, V1JobList, CoreV1Api, V1Status

from test.controllers.utils import del_env
from xcube_hub import api
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


class TestCubeGens(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')

    @patch('xcube_hub.core.callbacks.get_callback')
    @patch('xcube_hub.core.cubegens.logs')
    @patch('xcube_hub.core.cubegens.status')
    def test_get(self, status_p, logs_p, call_p):
        call_p.return_value = 100
        status_p.return_value = 'Ready'
        logs_p.return_value = ['bla']
        res = cubegens.get(user_id='drwho', cubegen_id='id')

        self.assertDictEqual({'cubegen_id': 'id', 'status': 'Ready', 'output': ['bla'], 'progress': 100}, res)

        status_p.return_value = None

        with self.assertRaises(api.ApiError) as e:
            cubegens.get(user_id='drwho', cubegen_id='id')

        self.assertEqual("Cubegen id not found", str(e.exception))
        self.assertEqual(404, e.exception.status_code)

        status_p.return_value = 'Ready'
        status_p.side_effect = ApiException(401, 'Unauthorized')

        with self.assertRaises(api.ApiError) as e:
            cubegens.get(user_id='drwho', cubegen_id='id')

        self.assertIn("Reason: Unauthorized", str(e.exception))
        self.assertIn("401", str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch('xcube_hub.core.cubegens.get')
    @patch.object(BatchV1Api, 'list_namespaced_job')
    def test_list(self, batch_p, get_p):
        batch_p.return_value = V1JobList(items=[V1Pod(metadata=V1ObjectMeta(name='drwho-cate-sdav'))])
        get_p.return_value = {'cubegen_id': 'id', 'status': 'Ready', 'output': ['bla'], 'progress': 100}
        res = cubegens.list('drwho')

        self.assertEqual(1, len(res))
        self.assertDictEqual({'cubegen_id': 'id', 'status': 'Ready', 'output': ['bla'], 'progress': 100}, res[0])

        batch_p.side_effect = ApiException(401, 'Unauthorized')

        with self.assertRaises(api.ApiError) as e:
            cubegens.list(user_id='drwho')

        self.assertIn("Reason: Unauthorized", str(e.exception))
        self.assertIn("401", str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch.object(CoreV1Api, 'list_namespaced_pod')
    @patch.object(CoreV1Api, 'read_namespaced_pod_log')
    def test_logs(self, pod_read_p, pod_p):
        pod_p.return_value = V1JobList(items=[V1Pod(metadata=V1ObjectMeta(name='drwho-cate-sdav'))])
        pod_read_p.return_value = 'bla'

        res = cubegens.logs('drwho')

        self.assertEqual(1, len(res))
        self.assertEqual(['bla',], res)

        pod_p.side_effect = ApiException(401, 'Unauthorized')

        with self.assertRaises(api.ApiError) as e:
            cubegens.logs('drwho', raises=True)

        self.assertIn("Reason: Unauthorized", str(e.exception))
        self.assertIn("401", str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch.object(BatchV1Api, 'delete_namespaced_job')
    def test_delete_one(self, batch_p):
        batch_p.return_value = V1Status(message='Ganz blöd', status=100)

        res = cubegens.delete_one('id')
        batch_p.assert_called_once()

        self.assertEqual(100, res)

        batch_p.side_effect = ApiException(401, 'Unauthorized')

        with self.assertRaises(api.ApiError) as e:
            cubegens.delete_one('id')

        self.assertIn("Reason: Unauthorized", str(e.exception))
        self.assertIn("401", str(e.exception))
        self.assertEqual(400, e.exception.status_code)


if __name__ == '__main__':
    unittest.main()
