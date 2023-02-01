#!/bin/bash

set -E

scripts/render-config.sh
exit_code=$?
if [ $exit_code != 0 ]; then
  echo "Error ${exit_code} encountered rendering the service configuration, NOT STARTING SERVER"
  exit 1
fi

echo "Running in DEV mode; server will reload when source changes"
poetry run uvicorn orcidlink.main:app --reload --host 0.0.0.0 --port 5000
