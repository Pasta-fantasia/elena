#!/bin/bash

python3 -m venv $HOME/venv

source $HOME/venv/bin/activate

echo "source $HOME/venv/bin/activate " >> $HOME/.bashrc

pip install -U pip setuptools wheel

pip install -r requirements.txt
