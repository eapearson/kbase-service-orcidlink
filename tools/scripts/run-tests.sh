tests="${1}"
test_file_path="src/test/${tests}"
export MODULE_DIR="${PWD}"
export MINIMAL_COVERAGE="${MINIMAL_COVERAGE:-90}"
echo "Running tests in path '${test_file_path}"
echo "  with MODULE_DIR of '${MODULE_DIR}'"
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