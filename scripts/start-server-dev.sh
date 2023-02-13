#!/bin/bash

scripts/render-config.sh
exit_code=$?
if [ $exit_code != 0 ]; then
  echo "Error ${exit_code} encountered rendering the service configuration, NOT STARTING SERVER"
  exit 1
fi


#
# Run initialization script.
# This script will carry out various tasks to ensure a good environment.
# E.g. check database connection, check database version, carry out any
# upgrades if necessary, ensure indexes are in place, etc.
#
scripts/service-initialization.sh
exit_code=$?
if [ $exit_code != 0 ]; then
  echo "Error ${exit_code} encountered during service initialization, NOT STARTING SERVER"
  exit 1
fi

echo "Running in DEV mode; server will reload when source changes"
poetry run uvicorn orcidlink.main:app --reload --host 0.0.0.0 --port 5000
