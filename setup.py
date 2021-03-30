# coding: utf-8

from setuptools import setup, find_packages

NAME = "xcube-hub"
VERSION = "2.1.0.dev1"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion>=2.0.2",
    "swagger-ui-bundle>=0.0.2",
    "python_dateutil>=2.6.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="xcube Generation API",
    author_email="info@brockmann-consult.de",
    url="",
    keywords=["OpenAPI", "xcube Generation API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['resources/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['xcube-hub=xcube_hub.__main__:main']},
    long_description="""\
    Restful API for handling xcube Services
    """
)

