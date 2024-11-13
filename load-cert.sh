#!/bin/bash
SCRIPT_PATH=$(dirname $0)
cd $SCRIPT_PATH
source .venv/bin/activate
python load-cert.py $@
deactivate