#! /usr/bin/env bash
# Reset this var to be sure no addons_path is find
export ADDONS_GIT_CLOUD_MODULES="False"
python3 --version
pip3 --version
pip3 install -U pip
pip3 install --no-input --disable-pip-version-check --no-python-version-warning --verbose  .
python3 -m unittest discover -s tests/tests_odoo -t ./
