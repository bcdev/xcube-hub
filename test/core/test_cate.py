import unittest
from unittest.mock import patch

from dotenv import load_dotenv
from kubernetes.client import V1ServiceList, V1Service, V1ObjectMeta, V1Pod, V1PodStatus, ApiException, V1Deployment

from test.controllers.utils import del_env
from xcube_hub import api
from xcube_hub.core import cate


class TestCubeGens(unittest.TestCase):
    def setUp(self) -> None:
        load_dotenv(dotenv_path='test/.env')

    def tearDown(self) -> None:
        del_env(dotenv_path='test/.env')

    @patch('xcube_hub.core.k8s.delete_deployment')
    @patch('xcube_hub.core.k8s.get_deployment')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    def test_delete_cate(self, namespace_p, get_p, delete_p):
        get_p.return_value = None
        res = cate.delete_cate('drwho')

        self.assertTrue(res)

        get_p.return_value = ['deployment', ]
        res = cate.delete_cate('drwho')

        delete_p.assert_called_once()
        self.assertTrue(res)

    @patch('xcube_hub.core.k8s.delete_service')
    @patch('xcube_hub.core.k8s.list_services')
    @patch('xcube_hub.core.k8s.get_deployment')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    def test_delete_cate_with_prune(self, namespace_p, get_p, list_p, service_p):
        get_p.return_value = None
        list_p.return_value = V1ServiceList(items=[])
        res = cate.delete_cate('drwho', prune=True)
        list_p.assert_called_once()
        self.assertTrue(res)

        list_p.return_value = V1ServiceList(items=[V1Service(metadata=V1ObjectMeta(name='drwho-cate'))])
        res = cate.delete_cate('drwho', prune=True)
        service_p.assert_called_once()
        self.assertTrue(res)

    @patch('xcube_hub.core.k8s.get_pod')
    def test_get_status(self, pod_p):
        pod_p.return_value = None
        res = cate.get_status('drwho')

        self.assertDictEqual({'phase': 'Unknown'}, res)

        pod_p.return_value = V1Pod(status=V1PodStatus(phase='Running'))
        res = cate.get_status('drwho')

        self.assertEqual('Running', res['phase'])

    @patch('xcube_hub.core.k8s.count_pods')
    def test_get_pod_count(self, ct_p):
        ct_p.return_value = 10
        res = cate.get_pod_count()

        self.assertDictEqual({'running_pods': 10}, res)


    @patch('xcube_hub.poller.poll_pod_phase')
    @patch('xcube_hub.core.k8s.create_ingress')
    @patch('xcube_hub.core.k8s.get_ingress')
    @patch('xcube_hub.core.k8s.create_service_if_not_exists')
    @patch('xcube_hub.core.k8s.create_deployment')
    @patch('xcube_hub.core.k8s.create_deployment_object')
    @patch('xcube_hub.core.k8s.count_pods')
    @patch('xcube_hub.core.user_namespaces.create_if_not_exists')
    @patch('xcube_hub.core.k8s.get_deployment')
    def test_launch_cate(self, get_p, namespace_p, ct_p, deployment_p,
                         deployment_create_p, service_create_p,
                         get_ingress_p, ingress_p, poll_p):
        with self.assertRaises(api.ApiError) as e:
            cate.launch_cate('drwho#######')

        self.assertEqual('Invalid user name.', str(e.exception))
        self.assertEqual('400', str(e.exception.status_code))

        ct_p.return_value = 100

        with self.assertRaises(api.ApiError) as e:
            cate.launch_cate('drwho')

        self.assertEqual('Too many pods running.', str(e.exception))
        self.assertEqual('413', str(e.exception.status_code))

        ct_p.return_value = 10

        get_p.return_value = None
        deployment_p.return_value = V1Deployment(metadata=V1ObjectMeta(name='drwho-cate'))
        res = cate.launch_cate('drwho')

        self.assertDictEqual({'serverUrl': 'https://stage.catehub.climate.esa.int/drwho'}, res)

        get_ingress_p.return_value = None
        res = cate.launch_cate('drwho')

        self.assertDictEqual({'serverUrl': 'https://stage.catehub.climate.esa.int/drwho'}, res)

        ct_p.side_effect = ApiException(400, 'test')
        with self.assertRaises(api.ApiError) as e:
            cate.launch_cate('drwho')

        self.assertIn('Reason: test', str(e.exception))
        self.assertEqual('400', str(e.exception.status_code))

