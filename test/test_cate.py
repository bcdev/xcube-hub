import unittest
from unittest.mock import patch
from test.config import TEST_PODS_EMPTY, TEST_PODS_RUNNING
from xcube_hub.controllers import cate


class MyTestCase(unittest.TestCase):
    @patch('kubernetes.client.CoreV1Api.list_pod_for_all_namespaces', return_value=TEST_PODS_EMPTY)
    def test_get_pod_count(self, m):
        expected_value = {'running_pods': 0}
        res = cate.get_pod_count()

        self.assertDictEqual(expected_value, res)

    @patch('kubernetes.client.CoreV1Api.list_namespaced_pod', return_value=TEST_PODS_EMPTY)
    def test_get_status_empty(self, m_list):
        expected_value = 'Unknown'
        status = cate.get_status('helge')
        self.assertEqual(expected_value, status['phase'])

    @patch('kubernetes.client.CoreV1Api.list_namespaced_pod', return_value=TEST_PODS_RUNNING)
    def test_get_status(self, m_list):
        expected_value = 'Running'
        status = cate.get_status('helge')
        self.assertEqual(expected_value, status['phase'])


if __name__ == '__main__':
    unittest.main()
