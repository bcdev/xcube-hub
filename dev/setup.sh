#!/usr/bin/env bash

source activate xcube-hub
pip install pydevd-pycharm~=211.7628.21
python setup.py develop
python xcube_hub/__main__.py
