#!/usr/bin/env bash

echo "* Running autoflake."
autoflake -r -i --remove-all-unused-imports --remove-unused-variables src
result_code=$?
if [[ $result_code -gt 0 ]]; then
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! autoflake found errors.                              "
  echo "! please address the errors, then run autoflake again. "
  echo "! Good Luck!                                           "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
else
  echo
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo "> autoflake finished successfully "
  echo "> Good to Go!                     "
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo
fi
exit $result_code