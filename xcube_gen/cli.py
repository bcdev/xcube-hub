# The MIT License (MIT)
# Copyright (c) 2020 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import click
from typing import Optional
from xcube_gen.version import version

# import pydevd_pycharm
# pydevd_pycharm.settrace('172.17.0.1', port=9000, stdoutToServer=True, stderrToServer=True)


@click.command(name="start")
@click.option('--address', '-a',
              help="The host address to listen on. "
                   "Set this to '0.0.0.0' to have the server available externally as well. "
                   "Defaults to  '127.0.0.1'.")
@click.option('--port', '-p', type=int,
              help="The port number to listen on. Defaults to 5000.")
@click.option('--debug', is_flag=True, help='Output extra debugging information.')
@click.option('--cache-provider', type=click.Choice(['redis', 'leveldb'], case_sensitive=False),
              help='Output extra debugging information.')
def start(address: Optional[str],
          port: Optional[int],
          debug: bool,
          cache_provider: str):
    """
    Start the service.
    """

    from xcube_gen.service import start
    start(host=address, port=port, debug=debug, cache_provider=cache_provider)


@click.command(name="stop")
def stop():
    """
    Stop the service.
    """
    print('Sorry, not implemented yet.')


# noinspection PyShadowingBuiltins,PyUnusedLocal
@click.group(name="genserv")
@click.version_option(version)
def cli():
    """
    xcube data cube generation service.
    """


cli.add_command(start)
cli.add_command(stop)


def main(args=None):
    # noinspection PyBroadException
    try:
        exit_code = cli.main(args=args, standalone_mode=False)
    except click.ClickException as e:
        e.show()
        exit_code = 1
    except Exception as e:
        import traceback
        traceback.print_exc()
        exit_code = 2
        print(f'Error: {e}')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
