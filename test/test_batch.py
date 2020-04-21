import unittest


class TestBatch(unittest.TestCase):
    def test_status(self):
        from xcube_gen.cfg import Batch

        batch = Batch(namespace='xcube-gen')
        res = batch.get_result('xcube-gen-7dc64f10-1697-455b-8c99-05b8a5b4742d')

        self.assertEqual(True, False)

    def test_get_pods(self):
        from xcube_gen.cfg import Batch

        batch = Batch(namespace='xcube-gen')
        logs = batch.get_pods("xcube-gen-7dc64f10-1697-455b-8c99-05b8a5b4742d")

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
