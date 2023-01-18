#!/bin/bash

set -e



# Nice to set this up for all future python code being run.
export PYTHONPATH="${PWD}/src"

exec "$@"