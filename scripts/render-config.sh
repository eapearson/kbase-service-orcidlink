#!/bin/bash

jinja render \
  -t templates/config.tmpl.toml \
  -o config/config.toml \
  -e KBASE_ENDPOINT=${KBASE_ENDPOINT} \
  -e ORCID_CLIENT_ID=${ORCID_CLIENT_ID} \
  -e ORCID_CLIENT_SECRET=${ORCID_CLIENT_SECRET} \
  -e MONGO_HOST=${MONGO_HOST} \
  -e MONGO_PORT=${MONGO_PORT} \
  -e MONGO_DATABASE=${MONGO_DATABASE} \
  -e MONGO_USERNAME=${MONGO_USERNAME} \
  -e MONGO_PASSWORD=${MONGO_PASSWORD}
