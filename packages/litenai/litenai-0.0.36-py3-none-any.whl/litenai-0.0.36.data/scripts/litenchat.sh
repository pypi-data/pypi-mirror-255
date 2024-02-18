#!/bin/bash

usage() { echo "Usage: $0" 1>&2; exit 1; }

litenchat=`which litenchat.py`
if [ -z "${litenchat}" ]; then
    echo "litenchat.py not found"
    exit 1
fi
echo "litenchat = ${litenchat}"
python ${litenchat}
