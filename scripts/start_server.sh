export PYTHONPATH="$PWD/src"
# we probably don't want to reload in prod, but this whole thing is
# currently just a prototype, so who cares.
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 5000