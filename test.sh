#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# setting python path as the script directory to make imports work fine
export PYTHONPATH=$SCRIPT_DIR 

coverage run -m pytest .