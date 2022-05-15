#!/bin/bash

# https://www.baeldung.com/linux/bash-ensure-instance-running
another_instance() {
    echo "There is another instance running, exiting" 1>>_out.log 2>>_err.log
    exit 1
}

#if [ "$(pgrep elena.sh)" != $$ ]; then
#     another_instance
#fi

source $HOME/venv/bin/activate

cd $HOME/elena

python elena_v1.py 1>>_out.log 2>>_err.log
