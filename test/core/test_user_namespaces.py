import unittest
from unittest.mock import patch

from kubernetes.client import CoreV1Api, ApiException, V1NamespaceList, V1Namespace, V1ObjectMeta

from xcube_hub import api
from xcube_hub.core import user_namespaces


class TestUSerNamespaces(unittest.TestCase):
    @patch.object(CoreV1Api, 'create_namespace')
    def test_create_if_not_exists(self, create_p):
        with patch('xcube_hub.core.user_namespaces.exists') as exists_p:
            exists_p.return_value = True
            res = user_namespaces.create_if_not_exists('drwho')

            create_p.assert_not_called()
            self.assertFalse(res)

            exists_p.return_value = False
            res = user_namespaces.create_if_not_exists('drwho')
            create_p.assert_called_once()
            self.assertTrue(res)

            create_p.side_effect = ApiException(500, 'Error')
            with self.assertRaises(api.ApiError) as e:
                user_namespaces.create_if_not_exists('drwho')

            self.assertEqual(400, e.exception.status_code)
            self.assertIn('500', str(e.exception))
            self.assertIn('Error', str(e.exception))

    @patch.object(CoreV1Api, 'list_namespace')
    def test_exists(self, list_p):
        list_p.return_value = V1NamespaceList(items=[])
        res = user_namespaces.exists('drwho')

        list_p.assert_called_once()
        self.assertFalse(res)

        list_p.return_value = V1NamespaceList(items=[V1Namespace(metadata=V1ObjectMeta(name='drwho'))])
        res = user_namespaces.exists('drwho')

        self.assertTrue(res)

        list_p.side_effect = ApiException(500, 'Error')
        with self.assertRaises(api.ApiError) as e:
            user_namespaces.create_if_not_exists('drwho')

        self.assertEqual(400, e.exception.status_code)
        self.assertIn('500', str(e.exception))
        self.assertIn('Error', str(e.exception))

    @patch.object(CoreV1Api, 'list_namespace')
    def test_list(self, list_p):
        list_p.return_value = V1NamespaceList(items=[])
        res = user_namespaces.list()

        list_p.assert_called_once()
        self.assertEqual(0, len(res))

        list_p.return_value = V1NamespaceList(items=[V1Namespace(metadata=V1ObjectMeta(name='drwho'))])
        res = user_namespaces.list()

        self.assertEqual(1, len(res))

        list_p.side_effect = ApiException(500, 'Error')
        with self.assertRaises(api.ApiError) as e:
            user_namespaces.list()

        self.assertEqual(400, e.exception.status_code)
        self.assertIn('500', str(e.exception))
        self.assertIn('Error', str(e.exception))

    @patch.object(CoreV1Api, 'delete_namespace')
    def test_delete(self, delete_p):
        res = user_namespaces.delete('drwho')

        delete_p.assert_called_once()
        self.assertTrue(res)

        delete_p.side_effect = ApiException(500, 'Error')
        with self.assertRaises(api.ApiError) as e:
            user_namespaces.delete('drwho')

        self.assertEqual(400, e.exception.status_code)
        self.assertIn('500', str(e.exception))
        self.assertIn('Error', str(e.exception))


if __name__ == '__main__':
    unittest.main()
