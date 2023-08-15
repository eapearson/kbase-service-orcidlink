#!/bin/bash

echo "* Running isort."
# Ge sure isort is on the last line, in order to return the result code, so that tooling can
# honor failure. Alternatively, one can capture the result code in $? and return it later.
isort src
result_code=$?
if [[ $result_code -gt 0 ]]; then
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! isort found errors.                              "
  echo "! please address the errors, then run isort again. "
  echo "! Good Luck!                                      "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
else
  echo
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo "> isort finished successfully"
  echo "> Good to Go!                "
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo
fi
exit $result_code