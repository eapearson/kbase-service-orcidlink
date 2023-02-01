#!/bin/bash

# We want to exit immediately if any env_var() call fails
set -E

jinja render \
  -t templates/config.toml.jinja \
  -o config/config.toml \
  -e KBASE_ENDPOINT="${KBASE_ENDPOINT:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e ORCID_OAUTH_BASE_URL="${ORCID_OAUTH_BASE_URL:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e ORCID_API_BASE_URL="${ORCID_API_BASE_URL:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e ORCID_CLIENT_ID="${ORCID_CLIENT_ID:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e ORCID_CLIENT_SECRET="${ORCID_CLIENT_SECRET:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e MONGO_HOST="${MONGO_HOST:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e MONGO_PORT="${MONGO_PORT:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e MONGO_DATABASE="${MONGO_DATABASE:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e MONGO_USERNAME="${MONGO_USERNAME:?Required environment variable KBASE_ENDPOINT absent or empty}" \
  -e MONGO_PASSWORD="${MONGO_PASSWORD:?Required environment variable KBASE_ENDPOINT absent or empty}"
