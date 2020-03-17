import unittest

from kubernetes import config


class TestBatch(unittest.TestCase):
    def setUp(self) -> None:
        config.load_kube_config()

    def test_status(self):
        from xcube_gen.batch import Batch

        batch = Batch()
        batch.get_status('xcube-gen-7dc64f10-1697-455b-8c99-05b8a5b4742d')
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
