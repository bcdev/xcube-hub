#/bin/bash

source activate xcube-hub
pip install pydevd-pycharm~=203.7148.57
mamba install -c conda-forge python-keycloak
python setup.py develop
python xcube_hub/__main__.py
