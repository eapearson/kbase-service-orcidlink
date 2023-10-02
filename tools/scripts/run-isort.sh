#!/usr/bin/env bash

subcommand=${1:-check}
target=${2:-src}
echo "Running isort ${subcommand} ${target}..."
if [ "${subcommand}" = "check" ]; then
  echo "CHECKING ${target}"
  isort --check ${target}
  result_code=$?
  if [[ $result_code -gt 0 ]]; then
    echo
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "! isort check found errors.                        "
    echo "! Please address the errors, then run isort again, "
    echo "! or simply run again with the 'format' option.    "
    echo "! Good Luck!                                       "
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo
  else
    echo
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "> isort check finished successfully. "
    echo "> Good to Go!                        "
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo
  fi
  exit $result_code
elif [ "${subcommand}" = "format" ]; then
  echo "FORMATTING ${target}"
  isort ${target}
  result_code=$?
  if [[ $result_code -gt 0 ]]; then
    echo
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "! isort formatting encountered errors.             "
    echo "! Please address the errors, then run isort again, "
    echo "! Good Luck!                                       "
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo
  else
    echo
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "> isort finished formatting successfully. "
    echo "> Good to Go!                             "
    echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo
  fi
  exit $result_code
else
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! unsupported subcommand '${subcommand}' "
  echo "! Please fix this, then run isort again. "
  echo "! Good Luck!                             "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
  exit 1
fi
