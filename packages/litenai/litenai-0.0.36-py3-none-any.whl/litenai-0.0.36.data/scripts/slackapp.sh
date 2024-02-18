#!/bin/bash
slackapp=`which slackapp.py`
if [ -z "${slackapp}" ]; then
    echo "slackapp.py not found"
    exit 1
fi
echo "Starting slack app ${slackapp}"
python ${slackapp}
