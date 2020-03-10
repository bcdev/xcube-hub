import unittest
from click.testing import CliRunner

from xcube_gen.cli import info


class CliTestCase(unittest.TestCase):
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(info)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "0.3.0.dev0\n")


if __name__ == '__main__':
    unittest.main()
