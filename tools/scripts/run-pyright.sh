#!/usr/bin/env bash

echo "* Running pyright."
# Ge sure pyright is on the last line, in order to return the result code, so that tooling can
# honor failure. Alternatively, one can capture the result code in $? and return it later.
pyright
result_code=$?
if [[ $result_code -gt 0 ]]; then
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! pyright found errors.                              "
  echo "! please address the errors, then run pyright again. "
  echo "! Good Luck!                                         "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
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