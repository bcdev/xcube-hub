#!/usr/bin/env bash

source activate xcube-hub
pip install pydevd-pycharm~=212.5080.55
pip uninstall -y xcube-hub
python setup.py develop
python xcube_hub/__main__.py
