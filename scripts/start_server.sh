export PYTHONPATH="$PWD/src"
if [ -z "${DEV}" ]; then
  poetry run uvicorn main:app --host 0.0.0.0 --port 5000
else
  poetry run uvicorn main:app --reload --host 0.0.0.0 --port 5000
fi