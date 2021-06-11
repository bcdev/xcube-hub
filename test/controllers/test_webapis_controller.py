import unittest
from unittest.mock import patch

from test import BaseTestCase
from xcube_hub import api
from xcube_hub.controllers import webapis


class TestWebapis(BaseTestCase):
    @patch('xcube_hub.core.cate.get_pod_count', create=True)
    def test_get_webapis(self, p):
        p.return_value = {'running_pods': 100}

        res = webapis.get_webapis()

        self.assertEqual(200, res[1])

        p.side_effect = api.ApiError(400, 'Error')

        res = webapis.get_webapis()

        self.assertEqual(400, res[1])
        self.assertEqual('Error', res[0]['message'])


if __name__ == '__main__':
    unittest.main()
