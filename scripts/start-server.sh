export PYTHONPATH="$PWD/src"
if [ -z "${DEV}" ]; then
  echo "Running in PROD mode; server will NOT reload when source changes"
  poetry run uvicorn orcidlink.main:app --host 0.0.0.0 --port 5000
else
  echo "Running in DEV mode; server will reload when source changes"
  poetry run uvicorn orcidlink.main:app --reload --host 0.0.0.0 --port 5000
fi