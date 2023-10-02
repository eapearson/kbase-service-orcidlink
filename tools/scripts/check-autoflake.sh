#!/usr/bin/env bash

echo "* Running autoflake check."
# Ge sure mypy is on the last line, in order to return the result code, so that tooling can
# honor failure. Alternatively, one can capture the result code in $? and return it later.
autoflake -r --quiet --check --remove-all-unused-imports --remove-unused-variables src
result_code=$?
if [[ $result_code -gt 0 ]]; then
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! autoflake would make changes                         "
  echo "! please address the errors, then run autoflake again. "
  echo "! Good Luck!                                      "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
else
  echo
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo "> mypy finished successfully "
  echo "> Good to Go!                "
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo
fi
exit $result_code