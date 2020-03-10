import unittest

from xcube_gen.process import process


class ProcessTest(unittest.TestCase):
    def test_process(self):
        # Just a smoke test
        response = process({})
        self.assertEqual({}, response)
