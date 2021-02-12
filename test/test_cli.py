import unittest
from click.testing import CliRunner

from xcube_hub_old.cli import cli
from xcube_hub_old.cli import start
from xcube_hub_old.cli import stop


class CliTest(unittest.TestCase):
    def test_cli(self):
        # Just a smoke test
        runner = CliRunner()
        result = runner.invoke(cli, '--help')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Usage: xcube-hub [OPTIONS] COMMAND [ARGS]...\n\n  '),
                        msg=result.output)

    def test_start(self):
        # Just a smoke test
        runner = CliRunner()
        result = runner.invoke(start, '--help')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Usage: start [OPTIONS]\n\n  Start the service.'),
                        msg=result.output)

    def test_stop(self):
        # Just a smoke test
        runner = CliRunner()
        result = runner.invoke(stop, '--help')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('Usage: stop [OPTIONS]\n\n  Stop the service.'),
                        msg=result.output)
