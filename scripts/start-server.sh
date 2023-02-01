#!/bin/bash

scripts/render-config.sh
exit_code=$?
if [ $exit_code != 0 ]; then
  echo "Error ${exit_code} encountered rendering the service configuration, NOT STARTING SERVER"
  exit 1
fi

echo "Running in PROD mode; server will NOT reload when source changes"
poetry run uvicorn orcidlink.main:app --host 0.0.0.0 --port 5000
