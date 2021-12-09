import base64
import unittest
from unittest.mock import Mock, patch, MagicMock

from kubernetes import client
from kubernetes.client import ApiException, V1ObjectMeta, CoreV1Api, V1PersistentVolumeClaimList, \
    V1PersistentVolumeClaim, ApiValueError, AppsV1Api, V1DaemonSet, V1DaemonSetList, V1Status, V1Deployment, \
    V1DeploymentList, V1ServiceList, NetworkingV1beta1Ingress, NetworkingV1beta1IngressList, V1Pod, V1PodList, \
    V1ConfigMap, V1Secret
from xcube_hub import api
from xcube_hub.core import k8s

from xcube_hub.core.k8s import create_pvc, delete_deployment, list_deployments, create_service, \
    delete_service, list_services, create_ingress, patch_ingress, delete_ingress, list_ingresses, list_pods, \
    create_service_object


def raise_api_exception(namespace, body):
    raise ApiException(500, 'Test')


class TestK8s(unittest.TestCase):
    def setUp(self) -> None:
        self._core_v1_api = client.CoreV1Api()
        self._networking_api = client.NetworkingV1beta1Api()
        self._apps_api = client.AppsV1Api()

    @patch.object(CoreV1Api, 'read_namespaced_secret')
    def test_get_secret(self, read_p):
        secret_success = V1Secret(
            data=dict(MY_SECRET=base64.b64encode("Olaf".encode()))
        )
        read_p.return_value = secret_success
        res = k8s.get_secret(name="test", secret_item="MY_SECRET", namespace="default")

        self.assertEqual("Olaf", res)

        with self.assertRaises(api.ApiError) as e:
            k8s.get_secret(name="test", secret_item="MY_SECRET_NOT", namespace="default")

        self.assertEqual("System Error: Secret MY_SECRET_NOT not found in secret test.", str(e.exception))

        read_p.side_effect = ApiValueError("Whatever")

        with self.assertRaises(api.ApiError) as e:
            k8s.get_secret(name="test", secret_item="MY_SECRET_NOT", namespace="default")

        self.assertEqual("Whatever", str(e.exception))

    def test_create_pvc_object(self):
        res = k8s.create_pvc_object('drwho')
        self.assertEqual('claim-drwho', res.metadata['name'])

    @patch.object(CoreV1Api, 'list_namespaced_persistent_volume_claim')
    def test_create_pvc_if_not_exists(self, list_p):
        pvc = V1PersistentVolumeClaim(metadata=V1ObjectMeta(name='tt'))
        list_p.return_value = V1PersistentVolumeClaimList(items=[pvc])

        res = k8s.create_pvc_if_not_exists(pvc, 'test_namespace')

        self.assertFalse(res)

        list_p.return_value = V1PersistentVolumeClaimList(items=[])
        with patch('xcube_hub.core.k8s.create_pvc') as p:
            res = k8s.create_pvc_if_not_exists(pvc, 'test_namespace')
            p.assert_called_once()

            self.assertTrue(res)

        list_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.create_pvc_if_not_exists(pvc, 'test_namespace')

        self.assertEqual('Error when creating the pvc tt: Error', str(e.exception))

    def test_create_pvc(self):
        self._core_v1_api.create_namespaced_persistent_volume_claim = Mock(side_effect=ApiException(500, 'Test'))
        pvc = client.V1PersistentVolumeClaim(
            metadata=V1ObjectMeta(name='workspace-nfs-pvc'),
        )

        with self.assertRaises(api.ApiError) as e:
            create_pvc(pvc, 'test', core_api=self._core_v1_api)

        expected = ("Error when creating the pvc workspace-nfs-pvc: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_create_goofys_daemonset_object(self):
        res = k8s.create_goofys_daemonset_object('test', 'drwho', [])

        self.assertEqual('test', res.metadata.name)

    @patch.object(AppsV1Api, 'create_namespaced_daemon_set')
    def test_create_goofys_daemonset(self, create_p):
        ds = V1DaemonSet(metadata=V1ObjectMeta(name='test'))
        k8s.create_goofys_daemonset(daemonset=ds)

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.create_goofys_daemonset(daemonset=ds)

        self.assertEqual('Error when creating the deployment test: Error', str(e.exception))

    @patch.object(AppsV1Api, 'list_namespaced_daemon_set')
    def test_list_goofys_daemonsets(self, create_p):
        ds = V1DaemonSet(metadata=V1ObjectMeta(name='test'))
        create_p.return_value = V1DaemonSetList(items=[ds])
        res = k8s.list_goofys_daemonsets(namespace='test')

        self.assertIsInstance(res, V1DaemonSetList)
        self.assertEqual(1, len(res.items))

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.list_goofys_daemonsets(namespace='test')

        self.assertEqual('Error when listing daemonsets in namespace test: Error', str(e.exception))

    @patch.object(AppsV1Api, 'list_namespaced_daemon_set')
    def test_get_goofys_daemonset(self, create_p):
        ds = V1DaemonSet(metadata=V1ObjectMeta(name='test'))
        create_p.return_value = V1DaemonSetList(items=[ds])
        res = k8s.get_goofys_daemonset(name='test', namespace='test')

        self.assertIsInstance(res, V1DaemonSet)
        self.assertEqual('test', res.metadata.name)

        create_p.return_value = V1DaemonSetList(items=[])
        res = k8s.get_goofys_daemonset(name='test', namespace='test')

        self.assertIsNone(res)

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.get_goofys_daemonset(name='test', namespace='test')

        self.assertEqual('Error when listing daemonsets in namespace test: Error', str(e.exception))

    @patch.object(AppsV1Api, 'delete_namespaced_daemon_set')
    def test_delete_goofys_daemonset(self, create_p):
        ds = V1DaemonSet(metadata=V1ObjectMeta(name='test'))
        create_p.return_value = V1Status(status='Deleted')
        res = k8s.delete_goofys_daemonset(name='test', namespace='test')

        create_p.assert_called_once()

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.delete_goofys_daemonset(name='test', namespace='test')

        self.assertEqual('Error when deleting the deployment test: Error', str(e.exception))

    @patch.object(AppsV1Api, 'list_namespaced_daemon_set')
    def test_create_goofys_daemonset_if_not_exists(self, create_p):
        ds = V1DaemonSet(metadata=V1ObjectMeta(name='test'))
        create_p.return_value = V1DaemonSetList(items=[ds])

        with patch('xcube_hub.core.k8s.create_goofys_daemonset') as p:
            k8s.create_goofys_daemonset_if_not_exists(daemonset=ds, namespace='test')

            p.assert_not_called()

            create_p.return_value = V1DaemonSetList(items=[])
            k8s.create_goofys_daemonset_if_not_exists(daemonset=ds, namespace='test')

            p.assert_called_once()

    def test_create_deployment_object(self):
        res = k8s.create_deployment_object(name='test', container_name='test', application='app', container_port=8080,
                                           image='cate')
        self.assertIsInstance(res, V1Deployment)
        self.assertEqual('test', res.metadata.name)

    @patch.object(AppsV1Api, 'create_namespaced_deployment')
    def test_create_deployment(self, create_p):
        pvc = client.V1Deployment(
            metadata=V1ObjectMeta(name='my-deployment'),
        )

        k8s.create_deployment(pvc, 'test')

        create_p.assert_called_once()

        create_p.side_effect = MagicMock(side_effect=ApiException(422, 'Test'))
        with self.assertRaises(api.ApiError) as e:
            k8s.create_deployment(pvc, 'test')

        expected = ("Error when creating the deployment my-deployment: (422)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(422, e.exception.status_code)

    @patch('xcube_hub.core.k8s.get_deployment')
    def test_create_deployment_if_exists(self, get_p):
        res = k8s.create_deployment_object(name='test', container_name='test', application='app', container_port=8080,
                                           image='cate')

        with patch('xcube_hub.core.k8s.create_deployment') as e:
            get_p.return_value = None
            k8s.create_deployment_if_not_exists(namespace='test', deployment=res)
            e.assert_called_once()

        with patch('xcube_hub.core.k8s.create_deployment') as e:
            get_p.return_value = True
            k8s.create_deployment_if_not_exists(namespace='test', deployment=res)
            e.assert_not_called()

    @patch.object(AppsV1Api, 'delete_namespaced_deployment')
    def test_delete_deployment(self, delete_p):
        delete_deployment('deployment', core_api=self._apps_api)
        delete_p.assert_called_once()

        delete_p.side_effect = ApiException('Test')

        with self.assertRaises(api.ApiError) as e:
            delete_deployment('deployment', core_api=self._apps_api)

        expected = ("Error when deleting the deployment deployment: (Test)\n"
                    "Reason: None\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch('xcube_hub.core.k8s.list_deployments')
    def test_get_deployment(self, list_p):
        deployment = k8s.create_deployment_object(name='test', container_name='test', application='application',
                                                  container_port=8080, image='cate')

        list_p.return_value = V1DeploymentList(items=[deployment])

        res = k8s.get_deployment(namespace='test', name='test')

        self.assertIsInstance(res, V1Deployment)
        self.assertEqual('test', res.metadata.name)

        list_p.return_value = V1DeploymentList(items=[])

        res = k8s.get_deployment(namespace='test', name='test')
        self.assertIsNone(res)

        list_p.side_effect = api.ApiError(400, 'Test')

        with self.assertRaises(api.ApiError) as e:
            k8s.get_deployment(namespace='test', name='test')

        self.assertEqual('Test', str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_list_deployments(self):
        self._apps_api.list_namespaced_deployment = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            list_deployments(namespace='test', core_api=self._apps_api)

        expected = ("Error when listing deployment in namespace test: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_create_service(self):
        self._core_v1_api.create_namespaced_service = Mock(side_effect=ApiException(500, 'Test'))

        service = client.V1Service(
            metadata=V1ObjectMeta(name='service'),
        )

        with self.assertRaises(api.ApiError) as e:
            create_service(service=service, namespace='test', core_api=self._core_v1_api)

        expected = ("Error when creating the service service: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch('xcube_hub.core.k8s.list_services')
    def test_create_service_if_not_exists(self, list_p):
        svc = create_service_object(name='test', port=8000, target_port=8000)

        with patch('xcube_hub.core.k8s.create_service') as p:
            list_p.return_value = V1ServiceList(items=[svc])

            k8s.create_service_if_not_exists(service=svc)
            p.assert_not_called()

            list_p.return_value = V1ServiceList(items=[])
            k8s.create_service_if_not_exists(service=svc)
            p.assert_called_once()

    def test_delete_service(self):
        self._core_v1_api.delete_namespaced_service = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            delete_service(name="service", namespace='test', core_api=self._core_v1_api)

        expected = ("Error when deleting the service service: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_list_services(self):
        self._core_v1_api.list_namespaced_service = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            list_services(namespace='test', core_api=self._core_v1_api)

        expected = ("Error when listing services in namespace test: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_create_ingress_object(self):
        res = k8s.create_ingress_object(name='test', service_name='test', service_port=8000, user_id='drwho',
                                        host_uri='https://test')

        self.assertIsInstance(res, NetworkingV1beta1Ingress)
        self.assertEqual('test', res.metadata.name)

    def test_create_ingress(self):
        self._networking_api.create_namespaced_ingress = Mock(side_effect=ApiException(500, 'Test'))

        ingress = client.NetworkingV1beta1Ingress(
            metadata=V1ObjectMeta(name='ingress'),
        )

        with self.assertRaises(api.ApiError) as e:
            create_ingress(ingress=ingress, namespace='test', core_api=self._networking_api)

        expected = ("Error when creating the ingress ingress: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_patch_ingress(self):
        self._networking_api.patch_namespaced_ingress = Mock(side_effect=ApiException(500, 'Test'))

        ingress = client.NetworkingV1beta1Ingress(
            metadata=V1ObjectMeta(name='ingress'),
        )

        with self.assertRaises(api.ApiError) as e:
            patch_ingress(name="ingress", namespace='test', body=ingress, core_api=self._networking_api)

        expected = ("Error when patching the ingress ingress: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_delete_ingress(self):
        self._networking_api.delete_namespaced_ingress = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            delete_ingress(name="ingress", namespace='test', core_api=self._networking_api)

        expected = ("Error when deleting the ingress ingress: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_list_ingresses(self):
        self._networking_api.list_namespaced_ingress = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            list_ingresses(namespace='test', core_api=self._networking_api)

        expected = ("Error when listing ingresses in namespace test: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    @patch('xcube_hub.core.k8s.list_ingresses')
    def test_get_ingress(self, list_p):
        ingress = k8s.create_ingress_object(name='test', service_name='test', service_port=8000, user_id='drwho',
                                            host_uri='https://test')

        list_p.return_value = NetworkingV1beta1IngressList(items=[ingress])

        res = k8s.get_ingress(namespace='test', name='test')

        self.assertIsInstance(res, NetworkingV1beta1Ingress)
        self.assertEqual('test', res.metadata.name)

        list_p.return_value = NetworkingV1beta1IngressList(items=[])

        res = k8s.get_ingress(namespace='test', name='test')
        self.assertIsNone(res)

    @patch('xcube_hub.core.k8s.list_ingresses')
    def test_create_ingress_if_not_exists(self, list_p):
        ingress = k8s.create_ingress_object(name='test', service_name='test', service_port=8000, user_id='drwho',
                                            host_uri='https://test')

        with patch('xcube_hub.core.k8s.create_ingress') as p:
            list_p.return_value = NetworkingV1beta1IngressList(items=[ingress])

            k8s.create_ingress_if_not_exists(ingress=ingress)
            p.assert_not_called()

            list_p.return_value = NetworkingV1beta1IngressList(items=[])
            k8s.create_ingress_if_not_exists(ingress=ingress)

    @patch('xcube_hub.core.k8s.list_pods')
    def test_get_pod(self, list_p):
        pod = V1Pod(metadata=V1ObjectMeta(name='test'))

        list_p.return_value = V1PodList(items=[pod])

        res = k8s.get_pod(namespace='test', prefix='test')

        self.assertIsInstance(res, V1Pod)
        self.assertEqual('test', res.metadata.name)

        list_p.return_value = V1PodList(items=[])

        res = k8s.get_pod(namespace='test', prefix='test')
        self.assertIsNone(res)

    @patch('xcube_hub.core.k8s.list_pods')
    def test_count_pods(self, list_p):
        pod = V1Pod(metadata=V1ObjectMeta(name='test'))

        list_p.return_value = V1PodList(items=[pod])

        res = k8s.count_pods(namespace='test')

        self.assertEqual(1, res)

        list_p.return_value = V1PodList(items=[])

        res = k8s.count_pods(namespace='test')

        self.assertEqual(0, res)

        list_p.return_value = None

        res = k8s.count_pods(namespace='test')

        self.assertEqual(0, res)

    @patch.object(CoreV1Api, 'list_namespaced_pod')
    @patch.object(CoreV1Api, 'list_pod_for_all_namespaces')
    def test_list_pods(self, list_all_p, list_p):
        pod = V1Pod(metadata=V1ObjectMeta(name='test',
                                          namespace='test_space',
                                          labels=dict(app='test_app')))

        def _side_effect(namespace:str, label_selector: str=None):
            if pod.metadata.namespace == namespace:
                if not label_selector:
                    return V1PodList(items=[pod])
                split_selector = label_selector.split('=')
                if pod.metadata.labels.get(split_selector[0], {}) \
                        == split_selector[1]:
                    return V1PodList(items=[pod])
            return V1PodList(items=[])

        def _side_effect_all(label_selector: str=None):
            if not label_selector:
                return V1PodList(items=[pod])
            split_selector = label_selector.split('=')
            if pod.metadata.labels.get(split_selector[0], {}) \
                    == split_selector[1]:
                return V1PodList(items=[pod])
            return V1PodList(items=[])

        list_p.side_effect = _side_effect
        list_all_p.side_effect = _side_effect_all

        res = list_pods(namespace='test_space', label_selector='app=test_app')
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(1, len(res.items))

        res = list_pods(namespace='quest_space', label_selector='app=test_app')
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(0, len(res.items))

        res = list_pods(namespace='test_space', label_selector='app=quest_app')
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(0, len(res.items))

        res = list_pods(label_selector='app=test_app')
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(1, len(res.items))

        res = list_pods(label_selector='app=quest_app')
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(0, len(res.items))

        res = list_pods()
        self.assertIsInstance(res, V1PodList)
        self.assertEqual(1, len(res.items))

        list_p.side_effect = ApiException('Test')
        list_all_p.side_effect = ApiException('Test')

        with self.assertRaises(api.ApiError) as e:
            list_pods(namespace='test')

        expected = ("Error when listing pods in namespace test: (Test)\n"
                    "Reason: None\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

        with self.assertRaises(api.ApiError) as e:
            list_pods()

        expected = ("Error when listing pods in namespace All: (Test)\n"
                    "Reason: None\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_create_configmap_object(self):
        data = {'dr': 'who'}
        res = k8s.create_configmap_object(name='test', data=data)

        self.assertIsInstance(res, V1ConfigMap)
        self.assertEqual('test', res.metadata.name)
        self.assertDictEqual(data, res.data)

    @patch.object(CoreV1Api, 'create_namespaced_config_map')
    def test_create_configmap(self, create_p):
        data = {'dr': 'who'}
        cm = k8s.create_configmap_object(name='test', data=data)

        k8s.create_configmap(namespace='test', body=cm)

        create_p.assert_called_once()

        create_p.side_effect = ApiValueError('Error')

        with self.assertRaises(api.ApiError) as e:
            k8s.create_configmap(namespace='test', body=cm)

        self.assertEqual('Error when creating the configmap test in test: Error', str(e.exception))


if __name__ == '__main__':
    unittest.main()
