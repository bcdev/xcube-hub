import unittest
from unittest.mock import patch

import kubernetes

from test.config import TEST_PODS, TEST_PODS_EMPTY
from xcube_hub.controllers import cate

pod = kubernetes.client.V1Pod(
    metadata=kubernetes.client.V1ObjectMeta(name='helge-cate-ascvhndasv'),
    status=kubernetes.client.V1PodStatus(phase='Running')
)

pods = kubernetes.client.V1PodList(items=[pod])
pods_empty = kubernetes.client.V1PodList(items=[])


class MyTestCase(unittest.TestCase):
    @patch('kubernetes.client.CoreV1Api.list_pod_for_all_namespaces', return_value=TEST_PODS_EMPTY)
    def test_get_pod_count(self, m):
        expected_value = {'running_pods': 0}
        res = cate.get_pod_count()

        self.assertDictEqual(expected_value, res)

    @patch('kubernetes.client.CoreV1Api.list_namespaced_pod', return_value=TEST_PODS)
    def test_get_status_empty(self, m_list):
        expected_value = 'Unknown'
        status = cate.get_status('helge')
        self.assertEqual(expected_value, status['phase'])

    @patch('kubernetes.client.CoreV1Api.list_namespaced_pod', return_value=pods)
    # @patch('kubernetes.client.V1Pod.status', return_value={'status': 'Running'})
    def test_get_status(self, m_list):
        expected_value = 'Running'
        status = cate.get_status('helge')
        self.assertEqual(expected_value, status['phase'])


if __name__ == '__main__':
    unittest.main()
