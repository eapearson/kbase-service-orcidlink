
tests="${1}"
test_file_path="src/test/${tests}"
echo "Running tests in path '${test_file_path}"
pytest -s --cov src/orcidlink --cov-report=html --cov-report=term --cov-report=lcov --cov-fail-under=99 "${test_file_path}"
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