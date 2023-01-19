#!/bin/bash

scripts/render-config.sh

echo "Running in PROD mode; server will NOT reload when source changes"
poetry run uvicorn orcidlink.main:app --host 0.0.0.0 --port 5000
