#!/usr/bin/env bash

source activate xcube-hub
pip install pydevd-pycharm~=213.5744.223
pip uninstall -y xcube-hub
python setup.py develop
python xcube_hub/__main__.py
