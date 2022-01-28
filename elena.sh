#!/bin/bash

source $HOME/venv/bin/activate

cd $HOME/elena

python elena_v1.py 1>>_out.log 2>>_err.log
