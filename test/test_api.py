import unittest

import xcube_gen.api as api


class ApiTest(unittest.TestCase):
    def test_datastores(self):
        # Just a smoke test
        response = api.datastores()
        self.assertIsInstance(response, dict)
