import json
import os
import unittest
from unittest.mock import patch, MagicMock

from dotenv import load_dotenv
from kubernetes.client import ApiException, BatchV1Api, V1Pod, V1ObjectMeta, V1JobList, CoreV1Api, V1Status, V1Job, \
    ApiValueError, V1JobStatus, V1JobCondition
from werkzeug.datastructures import FileStorage

from test.controllers.utils import del_env
from xcube_hub import api
from xcube_hub.cfg import Cfg
from xcube_hub.core import cubegens
from xcube_hub.core.cubegens import process_user_code, version
from xcube_hub.keyvaluedatabase import KeyValueDatabase
from xcube_hub.models.cubegen_config import CubegenConfig

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
    },
    'output_config': {}
}

_OUTPUT = """
{
    "result": {
        "dataset_descriptor": {
            "data_id": "test_cube.zarr",
            "type_specifier": "dataset",
            "crs": "WGS84",
            "bbox": [
                -2.24,
                51.99,
                -2.15,
                52.05
            ],
            "time_range": [
                "2020-12-01",
                "2021-02-28"
            ],
            "time_period": "1D",
            "dims": {
                "time": 90,
                "lat": 674,
                "lon": 1024
            },
            "spatial_res": 8.9e-05,
            "data_vars": {
                "B02": {
                    "name": "B02",
                    "dtype": "float32",
                    "dims": [
                        "time",
                        "lat",
                        "lon"
                    ]
                },
                "CLM": {
                    "name": "CLM",
                    "dtype": "float32",
                    "dims": [
                        "time",
                        "lat",
                        "lon"
                    ]
                }
            }
        },
        "size_estimation": {
            "image_size": [
                1024,
                674
            ],
            "tile_size": [
                512,
                512
            ],
            "num_variables": 5,
            "num_tiles": [
                2,
                1
            ],
            "num_requests": 900,
            "num_bytes": 1242316800
        }
    }
}
"""


class TestCubeGens(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')
        KeyValueDatabase.instance(provider='inmemory')
        Cfg.load_config()

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')
        import glob
        file_list = glob.glob("test/drwho*.yaml")
        for f in file_list:
            os.remove(f)

        file_list = glob.glob("test/id*.json")
        for f in file_list:
            os.remove(f)

    @patch('xcube_hub.core.callbacks.get_callback')
    @patch('xcube_hub.core.cubegens.logs')
    @patch('xcube_hub.core.cubegens.status')
    @patch('xcube_hub.core.cubegens.cubegens_result', create=True)
    def test_get(self, res_p, status_p, logs_p, call_p):
        call_p.return_value = 100
        status_p.return_value = 'Ready'
        logs_p.return_value = ['bla']
        res_p.return_value = {'status_code': 200, 'result': {}}
        res, status_code = cubegens.get(user_id='drwho', cubegen_id='id')

        expected = {'job_id': 'id',
                    'job_status': 'Ready',
                    'message': '',
                    'job_result': {'status_code': 200,
                                   'result': {},
                                   'output': ['bla']},
                    'output': ['bla'], 'progress': 100}

        self.assertDictEqual(
            expected,
            res)

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
        get_p.return_value = {'jobs_id': 'id', 'status': 'Ready', 'output': ['bla'], 'progress': 100}, 200
        res = cubegens.list('drwho')

        self.assertEqual(1, len(res[0]))
        self.assertDictEqual({'jobs_id': 'id', 'status': 'Ready', 'output': ['bla'], 'progress': 100}, res[0][0])

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
        self.assertEqual(['bla', ], res)

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

        batch_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            cubegens.delete_one('id')

        self.assertEqual("Error", str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch.object(BatchV1Api, 'read_namespaced_job_status')
    def test_status(self, batch_p):
        batch_p.return_value = V1Job(metadata=V1ObjectMeta(name='id-cate'), status=V1Status(message='Ganz blöd',
                                                                                            status=100))
        res = cubegens.status('id')
        batch_p.assert_called_once()

        self.assertEqual(100, res['status'])

        batch_p.side_effect = ApiValueError("Missing the required parameter `namespace` "
                                            "when calling `read_namespaced_job_status`")

        res = cubegens.status('id')

        self.assertDictEqual({}, res)

    @patch.object(BatchV1Api, 'read_namespaced_job_status')
    def test_info(self, batch_p):
        batch_p.return_value = V1Job(metadata=V1ObjectMeta(name='id-cate'), status=V1Status(message='Ganz blöd',
                                                                                            status=100))
        res = cubegens.status('id')
        batch_p.assert_called_once()

        self.assertEqual(100, res['status'])

        batch_p.side_effect = ApiValueError("Missing the required parameter `namespace` "
                                            "when calling `read_namespaced_job_status`")

        res = cubegens.status('id')

        self.assertDictEqual({}, res)

    def test_create_cubegen_object(self):
        cubegen = cubegens.create_cubegen_object('id', _CFG)

        self.assertIsInstance(cubegen, V1Job)
        self.assertEqual(1, len(cubegen.spec.template.spec.containers))
        self.assertEqual(2, len(cubegen.spec.template.spec.volumes))
        self.assertDictEqual({'name': 'xcube-hub-stores', 'configMap': {'name': 'xcube-hub-stores'}},
                             cubegen.spec.template.spec.volumes[0])

        container = cubegen.spec.template.spec.containers[0]
        self.assertEqual('id', cubegen.metadata.name)
        self.assertDictEqual({"app": "xcube-gen"}, cubegen.spec.template.metadata.labels)
        self.assertEqual("quay.io/bcdev/xcube-gen:0.7.2.dev0", container.image)
        self.assertEqual(2, len(container.volume_mounts))
        self.assertDictEqual({'mountPath': '/etc/xcube-hub', 'name': 'xcube-hub-stores', 'readOnly': True},
                             container.volume_mounts[0])

        with self.assertRaises(api.ApiError) as e:
            # noinspection PyTypeChecker
            cubegens.create_cubegen_object('id', None)

        self.assertEqual("create_gen_cubegen_object needs a config dict.", str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch('xcube_hub.core.cubegens.info')
    @patch.object(BatchV1Api, 'create_namespaced_job')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    def test_create_info_only(self, namespace_p, create_p, status_p):
        res, status_code = cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=True)

        self.assertIn("drwho-", res['job_id'])
        self.assertEqual(24, len(res['job_id']))

        create_p.side_effect = ApiException(401, 'Unauthorized')

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=True)

        self.assertEqual(400, e.exception.status_code)
        self.assertIn("Reason: Unauthorized", str(e.exception))
        self.assertIn("401", str(e.exception))

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=True)

        self.assertEqual(400, e.exception.status_code)
        self.assertEqual("Error", str(e.exception))

        del os.environ['XCUBE_HUB_CALLBACK_URL']

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=True)

        self.assertEqual('XCUBE_HUB_CALLBACK_URL must be given', str(e.exception))

        cfg = _CFG.copy()
        del cfg['input_config']

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', cfg, info_only=True)

        self.assertEqual("Either 'input_config' or 'input_configs' must be given", str(e.exception))

    @patch('xcube_hub.core.cubegens.info')
    @patch.object(BatchV1Api, 'create_namespaced_job')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    def test_create(self, namespace_p, create_p, info_p):
        info_p.return_value = {'result': {'cost_estimation': {'required': 1, 'available': 10000000}}}, 200

        res, status_code = cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertIn("drwho-", res['job_id'])
        self.assertEqual(24, len(res['job_id']))

        info_p.return_value = {'result': {'cost_estimation': {'required': 20, 'available': 10}}}, 200

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertEqual('Number of required punits (20) is greater than the available (10).', str(e.exception))

        info_p.return_value = {'result': {'cost_estimation': {'required': 3000, 'available': 4000}}}, 200

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertEqual('Number of required punits (3000) is greater than the absolute limit of 1000.',
                         str(e.exception))

    def test_process_user_code(self):
        cfg = {
            "input_configs": [
                {
                    "store_id": "@test",
                    "data_id": "DATASET-1.zarr"
                }
            ],
            "cube_config": {
            },
            "code_config": {
                "file_set": {
                    "path": ""
                },
                "callable_ref": "processor:process_dataset",
                "callable_params": {
                    "output_var_name": "X",
                    "input_var_name_1": "A",
                    "input_var_name_2": "B",
                    "factor_1": 0.4,
                    "factor_2": 0.2
                }
            },
            "output_config": {
                "store_id": "@test",
                "data_id": "OUTPUT.zarr",
                "replace": True
            }
        }

        cfg = CubegenConfig.from_dict(cfg)

        with patch('os.mkdir') as p:
            res = process_user_code(cfg=cfg, user_code=None)

            self.assertDictEqual(cfg.to_dict(), res.to_dict())
            p.assert_not_called()

        with patch('os.mkdir') as p:
            user_code = FileStorage(filename='test.zip')
            user_code.save = MagicMock()

            res = process_user_code(cfg=cfg, user_code=user_code)

            self.assertIn('test.zip', res.code_config.file_set.path)
            user_code.save.assert_called_once()
            p.assert_called_once()

    @patch('xcube_hub.core.cubegens.info')
    @patch.object(BatchV1Api, 'create_namespaced_job')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    def test_create_with_file(self, namespace_p, create_p, info_p):
        info_p.return_value = {'result': {'cost_estimation': {'required': 1, 'available': 10000000}}}, 200

        res, status_code = cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertIn("drwho-", res['job_id'])
        self.assertEqual(24, len(res['job_id']))

        info_p.return_value = {'result': {'cost_estimation': {'required': 20, 'available': 10}}}, 200

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertEqual('Number of required punits (20) is greater than the available (10).', str(e.exception))

        info_p.return_value = {'result': {'cost_estimation': {'required': 3000, 'available': 4000}}}, 200

        with self.assertRaises(api.ApiError) as e:
            cubegens.create('drwho', 'drwho@mail.org', _CFG, info_only=False)

        self.assertEqual('Number of required punits (3000) is greater than the absolute limit of 1000.',
                         str(e.exception))

    @patch('xcube_hub.core.punits.get_punits')
    @patch('xcube_hub.core.cubegens.get')
    @patch('xcube_hub.core.cubegens.create')
    @patch.object(BatchV1Api, 'read_namespaced_job_status')
    @patch('xcube_hub.core.cubegens.cubegens_result', create=True)
    def test_info2(self, res_p, status_p, create_p, get_p, punits_p):
        self.maxDiff = None
        res_p.return_value = {'status_code': 200, 'result': json.loads(_OUTPUT)['result']}
        status_p.return_value = V1Job(status=V1JobStatus(conditions=[V1JobCondition(type='Complete', status='ready')]))
        create_p.return_value = {'job_id': 'id', 'status': V1JobStatus().to_dict()}, 200

        get_p.return_value = {'job_id': 'id', 'job_status': 'success', 'result': {'status_code': 200},
                              'status': 'ready', 'output': ["bla", ], 'progress': 100}, 200

        punits_p.return_value = dict(punits=dict(total_count=1000), count=500, result=dict())

        with open('test/id.json', 'w') as f:
            f.write(_OUTPUT)

        res, status_code = cubegens.info(user_id='drwho', email='drwho@mail.org', body=_CFG, token='fdsvdf')

        expected = {'status_code': 200, 'result': {'dataset_descriptor': {'data_id': 'test_cube.zarr', 'type_specifier': 'dataset', 'crs': 'WGS84', 'bbox': [-2.24, 51.99, -2.15, 52.05], 'time_range': ['2020-12-01', '2021-02-28'], 'time_period': '1D', 'dims': {'time': 90, 'lat': 674, 'lon': 1024}, 'spatial_res': 8.9e-05, 'data_vars': {'B02': {'name': 'B02', 'dtype': 'float32', 'dims': ['time', 'lat', 'lon']}, 'CLM': {'name': 'CLM', 'dtype': 'float32', 'dims': ['time', 'lat', 'lon']}}}, 'size_estimation': {'image_size': [1024, 674], 'tile_size': [512, 512], 'num_variables': 5, 'num_tiles': [2, 1], 'num_requests': 900, 'num_bytes': 1242316800}, 'cost_estimation': {'required': 540, 'available': 500, 'limit': 1000}}, 'output': ['bla']}

        self.assertDictEqual(expected, res)

        ### Test limits not in correct format

        os.environ['GENERATOR_PROCESS_LIMIT'] = 'sdfsdf'

        with self.assertRaises(api.ApiError) as e:
            cubegens.info(user_id='drwho', email='drwho@mail.org', body=_CFG, token='fdsvdf')

        self.assertEqual("could not convert string to float: 'sdfsdf'", str(e.exception))

        os.environ['GENERATOR_PROCESS_LIMIT'] = '1000'

        punits_p.return_value = dict(punits=dict(total_count=1000))

        with self.assertRaises(api.ApiError) as e:
            cubegens.info(user_id='drwho', email='drwho@mail.org', body=_CFG, token='fdsvdf')

        self.assertEqual("Error. Cannot handle punit data. Entry 'count' is missing.", str(e.exception))
        punits_p.return_value = dict(punits=dict(total_count=1000), count=500)

        cfg = _CFG.copy()
        del cfg['input_config']

        with self.assertRaises(api.ApiError) as e:
            cubegens.info(user_id='drwho', email='drwho@mail.org', body=cfg, token='fdsvdf')

        self.assertEqual("Error. Invalid input configuration.", str(e.exception))

        cfg = _CFG.copy()
        # noinspection PyTypeChecker
        cfg['input_configs'] = [_CFG['input_config']]

        res, status_code = cubegens.info(user_id='drwho', email='drwho@mail.org', body=cfg, token='fdsvdf')

        self.assertEqual(expected, res)

    @patch('xcube_hub.core.cubegens.get')
    @patch('xcube_hub.core.cubegens.create')
    @patch.object(BatchV1Api, 'read_namespaced_job_status')
    def test_info2_error_response(self, status_p, create_p, get_p):
        status_p.return_value = V1Job(status=V1JobStatus(conditions=[V1JobCondition(type='Failed', status='error')]))
        create_p.return_value = \
            {'job_id': 'id', 'status': V1JobStatus().to_dict()}, \
            404

        get_p.return_value = {'job_id': 'id',
                              'result': {'status_code': 404},
                              'status': 'error',
                              'output': ["bla", ],
                              'message': 'something is wrong',
                              'progress': 100}, 404

        with self.assertRaises(api.ApiError) as e:
            cubegens.info(user_id='drwho',
                          email='drwho@mail.org',
                          body=_CFG,
                          token='fdsvdf')
        self.assertEqual("something is wrong",
                         str(e.exception))

    @patch.object(BatchV1Api, 'create_namespaced_job')
    def test_create_version(self, p_create):
        res, status_code = cubegens.create_version('drwho')

        self.assertIn('drwho', res['job_id'])
        self.assertEqual(200, status_code)

        p_create.side_effect = ApiException("test")

        with self.assertRaises(api.ApiError) as e:
            cubegens.create_version('drwho')

        self.assertEqual('(test)\nReason: None\n', str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch.object(BatchV1Api, 'read_namespaced_job_status')
    @patch('xcube_hub.core.cubegens.create_version')
    @patch('xcube_hub.core.cubegens.logs')
    def test_versions(self, p_logs, p_create_version, p_status):
        p_create_version.return_value = {'job_id': 'drwho-abc'}, 200
        p_logs.return_value = ['xcube: v1.0', '', 'xcube-sh: v1.0', '']
        p_status.return_value = V1Job(status=V1JobStatus(conditions=[V1JobCondition(status='Ready', type='Complete')]))

        res, status_code = version('drwho')
        expected = {'result': ['xcube: v1.0', 'xcube-sh: v1.0']}
        self.assertEqual(expected, res)
        self.assertEqual(200, status_code)

        p_status.side_effect = ApiValueError('error')

        with self.assertRaises(api.ApiError) as e:
            version('drwho')

        self.assertEqual('error', str(e.exception))
        self.assertEqual(400, e.exception.status_code)


if __name__ == '__main__':
    unittest.main()
