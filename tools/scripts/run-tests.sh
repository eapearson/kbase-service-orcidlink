#!/usr/bin/env bash

tests="${1}"
test_file_path="src/test/${tests}"
export TEST_DATA_DIR="${PWD}/test/data"
export SERVICE_DIRECTORY="${PWD}"
export MINIMAL_COVERAGE="${MINIMAL_COVERAGE:-90}"
echo "Test Data Dir is ${TEST_DATA_DIR}"
echo "Running tests in path '${test_file_path}"
echo "  with SERVICE_DIRECTORY of '${SERVICE_DIRECTORY}'"
pytest -s \
  --cov src/orcidlink \
  --cov-report=html \
  --cov-report=term \
  --cov-report=lcov \
  --cov-fail-under="${MINIMAL_COVERAGE}" \
  "${test_file_path}"
result_code=$?

if [[ $result_code -gt 0 ]]; then
  echo
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "! tests found errors.                             "
  echo "! please address the errors, then run tests again. "
  echo "! Good Luck!                                      "
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo
else
  echo
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo "> tests finished successfully "
  echo "> Good to Go!                "
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  echo
fi
exit $result_code