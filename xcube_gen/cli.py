# The MIT License (MIT)
# Copyright (c) 2019 by the xcube development team and contributors
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
from kubernetes import config, client

from xcube_gen.version import version


def create_job_object():
    # Configureate Pod template container
    container = client.V1Container(
        name="xcube",
        image="quay.io/bcdev/xcube-python-deps:0.3.0",
        command=["bash", "-c", "source activate xcube && xcube"])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "xcube"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4)
    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name='xcub3e'),
        spec=spec)

    return job


@click.command(name="info")
def info():
    """
    An xcube plug-in that implements a data cube generation service.
    """
    print(version)


@click.command(name="launch-job")
def launch_job():
    """
    An xcube plug-in that implements a data cube generation service.
    """
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    job = create_job_object()
    api_response = batch_v1.create_namespaced_job(
        body=job,
        namespace="default")
    print("Job created. status='%s'" % str(api_response.status))


# noinspection PyShadowingBuiltins,PyUnusedLocal
@click.group(name="gen")
@click.version_option(version)
def cli():
    """
    Cube generation tools for xcube.
    """


cli.add_command(info)
cli.add_command(launch_job)


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
