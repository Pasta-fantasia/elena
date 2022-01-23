#!/bin/bash

source $HOME/venv/bin/activate

cd $HOME/elena

python elena_v1.py 1>>elena_out.log 2>>elena_err.log
