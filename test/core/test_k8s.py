import unittest
from unittest.mock import Mock

from kubernetes import client
from kubernetes.client import ApiException, V1ObjectMeta
from xcube_hub import api

from xcube_hub.core.k8s import create_pvc, create_deployment, delete_deployment, list_deployments, create_service, \
    delete_service, list_services, create_ingress, patch_ingress, delete_ingress, list_ingresses, list_pods


def raise_api_exception(namespace, body):
    raise ApiException(500, 'Test')


class TestK8s(unittest.TestCase):
    def setUp(self) -> None:
        self._core_v1_api = client.CoreV1Api()
        self._networking_api = client.NetworkingV1beta1Api()
        self._apps_api = client.AppsV1Api()

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

    def test_create_deployment(self):
        self._apps_api.create_namespaced_deployment = Mock(side_effect=ApiException(500, 'Test'))
        pvc = client.V1Deployment(
            metadata=V1ObjectMeta(name='deployment'),
        )

        with self.assertRaises(api.ApiError) as e:
            create_deployment(pvc, 'test', core_api=self._apps_api)

        expected = ("Error when creating the deployment deployment: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_delete_deployment(self):
        self._apps_api.delete_namespaced_deployment = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            delete_deployment('deployment', core_api=self._apps_api)

        expected = ("Error when deleting the deployment deployment: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
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

    def test_list_pods(self):
        self._core_v1_api.list_namespaced_pod = Mock(side_effect=ApiException(500, 'Test'))
        self._core_v1_api.list_pod_for_all_namespaces = Mock(side_effect=ApiException(500, 'Test'))

        with self.assertRaises(api.ApiError) as e:
            list_pods(namespace='test', core_api=self._core_v1_api)

        expected = ("Error when listing pods in namespace test: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)

        with self.assertRaises(api.ApiError) as e:
            list_pods(core_api=self._core_v1_api)

        expected = ("Error when listing pods in namespace All: (500)\n"
                    "Reason: Test\n")
        self.assertEqual(expected, str(e.exception))
        self.assertEqual(400, e.exception.status_code)


if __name__ == '__main__':
    unittest.main()
