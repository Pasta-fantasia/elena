#!/bin/bash



# Git user -- recommended
# git config --global user.name "$name"
# git config --global user.email "$email"
# git config --global push.default simple

python3 -m venv $HOME/venv

source $HOME/venv/bin/activate

pip install -U pip setuptools wheel

pip install -r requirements.txt


