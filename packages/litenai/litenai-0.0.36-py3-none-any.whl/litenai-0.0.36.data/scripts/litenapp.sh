#!/bin/bash
host="localhost"
port="8220"

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--host)
      host="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--port)
      port="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done


usage() { echo "Usage: $0  [-h <host-ip>] [-p <port>]" 1>&2; exit 1; }

litenapp=`which litenapp.py`
if [ -z "${litenapp}" ]; then
    echo "litenapp.py not found"
    exit 1
fi
echo "Starting flask app ${litenapp} at ${host}:${port}"
flask --app=${litenapp}  run -h ${host} -p ${port}
