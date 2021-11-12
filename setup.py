# coding: utf-8

from setuptools import setup, find_packages

NAME = "xcube-hub"
version = None
with open('xcube_hub/version.py') as f:
    exec(f.read())

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = []

setup(
    name=NAME,
    version=version,
    description="xcube Generation API",
    author_email="info@brockmann-consult.de",
    url="",
    keywords=["OpenAPI", "xcube Generation API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['resources/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['xcube-hub=xcube_hub.cli:main']},
    long_description="""\
    Restful API for handling xcube Services
    """
)

