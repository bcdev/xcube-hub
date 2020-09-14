import unittest
from unittest.mock import patch

from xcube_gen.controllers import cate


class MyTestCase(unittest.TestCase):
    @patch('kubernetes.client.CoreV1Api.list_pod_for_all_namespaces', return_value=[])
    def test_get_pod_count(self, m):
        expected_value = {'running_pods': 0}
        res = cate.get_pod_count()

        self.assertDictEqual(expected_value, res)

    @patch('kubernetes.client.CoreV1Api.list_namespaced_pod', return_value=[])
    @patch('kubernetes.client.V1Pod.status', return_value={'status': 'Running'})
    def test_get_status(self, m_list, m_status):
        expected_value = {'status': 'Running'}
        status = cate.get_status('helge')
        self.assertDictEqual(expected_value, status)


if __name__ == '__main__':
    unittest.main()
