#!/bin/bash

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  dockerize -template ./templates/config.yaml.tmpl:./config/config.yaml
  sh ./scripts/start-server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  cp ./compile_report.json ./work/compile_report.json
  echo "Compilation Report copied to ./work/compile_report.json"
else
  echo Unknown
fi
