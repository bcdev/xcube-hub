#!/usr/bin/env python3

# The MIT License (MIT)
# Copyright (c) 2020 by Brockmann Consult GmbH
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


from setuptools import setup, find_packages
from xcube_hub_old.version import version

requirements = [
    "connexion",
    # Use ./environment.yml for deps.
]

packages = find_packages(exclude=["test", "test.*"])


setup(
    name="xcube_hub",
    version=version,
    description='A webapi that manages webservices to be deployed in a kubernetes cluster',
    license='MIT',
    author='xcube Development Team',
    packages=packages,
    author_email="info@brockmann-consult.de",
    package_data={
        '': ['swagger/swagger.yaml'],
        'xcube_gen.resources': ['datastores.json'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            # xcube's CLI
            'xcube-hub = xcube_hub.cli:main',
            'xcube_hub=xcube_hub.__main__:main'
        ],
    },
    install_requires=requirements,
)
