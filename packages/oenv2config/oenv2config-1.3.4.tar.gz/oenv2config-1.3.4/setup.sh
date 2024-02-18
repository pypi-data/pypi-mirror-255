#! /usr/bin/zsh
echo "Setup virtualenv"
pyenv install 3.11 -s
pyenv virtualenv 3.11 oenv2config
pyenv activate oenv2config

echo "Installing"
pip install --upgrade pip
pip install -e .
pip install -r ./mkdocs-plugins.txt

echo "Installing pre-commit"
pre-commit install

echo "Run unittest"
python -m unittest

echo "Build mkdocs"
mkdocs build

echo "Build antora"
antora .local-antora-playbook.yml
