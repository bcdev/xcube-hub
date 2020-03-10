import unittest

from xcube_gen.service import new_app


class ServiceTest(unittest.TestCase):
    def test_new_app(self):
        # Just a smoke test
        app = new_app()
        self.assertIsNotNone(app)
