#/bin/bash

source activate xcube-hub
pip install python-keycloak pydevd-pycharm~=203.7148.57
python setup.py develop
python xcube_hub/__main__.py
