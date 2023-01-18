#!/bin/bash

scripts/render-config.sh

echo "Running in DEV mode; server will reload when source changes"
poetry run uvicorn orcidlink.main:app --reload --host 0.0.0.0 --port 5000
