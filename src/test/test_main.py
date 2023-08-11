import json
import os
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from test.mocks.testing_utils import generate_kbase_token
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from orcidlink.lib import errors, utils
from orcidlink.lib.logger import log_event
from orcidlink.main import app

client = TestClient(app, raise_server_exceptions=False)

kbase_yaml = load_data_file("kbase1.yml")

INVALID_TOKEN = generate_kbase_token("invalid_token")
EMPTY_TOKEN = ""
NO_TOKEN = generate_kbase_token("no_token")
BAD_JSON = generate_kbase_token("bad_json")
TEXT_JSON = generate_kbase_token("text_json")
CAUSES_INTERNAL_ERROR = generate_kbase_token("something_bad")


@pytest.fixture
def fake_fs(fs):
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


TEST_LINK = load_data_json("link1.json")


# Happy paths


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_startup(fake_fs):
    with TestClient(app, raise_server_exceptions=False) as client:
        log_id = log_event("foo", {"bar": "baz"})
        assert isinstance(log_id, str)
        with open("/tmp/orcidlink.log", "r") as fin:
            log = json.load(fin)
        assert log["event"]["name"] == "foo"
        assert log["event"]["data"] == {"bar": "baz"}


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_docs(fake_fs):
    response = client.get("/docs")
    assert response.status_code == 200


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_docs_error(fake_fs):
    openapi_url = app.openapi_url
    app.openapi_url = None
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/docs")
    assert response.status_code == 404
    # TODO: test assertions about this..
    app.openapi_url = openapi_url


# Error conditions


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_main_404(fake_fs):
    response = client.get("/foo")
    assert response.status_code == 404


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_validation_exception_handler(fake_fs):
    response = client.post("/orcid/works", json={"foo": "bar"})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    content = response.json()
    assert content["code"] == errors.ERRORS.request_validation_error.code
    assert content["title"] == errors.ERRORS.request_validation_error.title
    assert (
        content["message"]
        == "This request does not comply with the schema for this endpoint"
    )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_kbase_auth_exception_handler(fake_fs):
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT) as [_, _, url, port]:
            # call with missing token
            response = client.get("/link", headers={})
            assert response.status_code == 422
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.request_validation_error.code
            assert content["title"] == errors.ERRORS.request_validation_error.title
            assert (
                content["message"]
                == "This request does not comply with the schema for this endpoint"
            )

            # call with invalid token
            response = client.get("/link", headers={"Authorization": INVALID_TOKEN})
            assert response.status_code == 401
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.authorization_required.code

            # TODO: the new ServiceErrorXX does not emit the title, as it is not part of the
            # JSON-RPC error structure. We want to be compatible with that, as it makes error
            # handling easier, generally.
            # assert content["title"] == "Invalid KBase Token"

            # Call with actual empty token; should be caught at the validator boundary
            # as it is invalid according to the rules for tokens.
            response = client.get("/link", headers={"Authorization": ""})
            assert response.status_code == 422
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.request_validation_error.code
            assert content["title"] == errors.ERRORS.request_validation_error.title

            # Call with actual empty token; should be caught at the validator boundary
            # as it is invalid according to the rules for tokens.
            response = client.get("/link", headers={})
            assert response.status_code == 422
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.request_validation_error.code
            assert content["title"] == errors.ERRORS.request_validation_error.title

            # # This one pretends that the /link implementation does not check for
            # # missing token first, but rather sends the no token. For testing
            # # this is implemented by sending a special testing token that triggers
            # # the appropriate response from the mock auth service.
            # # However, as this cannot be triggered in real usage, we should redo
            # # this test in a test of the client itself.
            # response = client.get("/link", headers={"Authorization": NO_TOKEN})
            # assert response.status_code == 401
            # assert response.headers["content-type"] == "application/json"
            # content = response.json()
            # assert content["code"] == "authorizationRequired"
            # assert content["title"] == "Authorization Required"

            # # call with empty token
            # # SAME HERE
            # response = client.get("/link", headers={"Authorization": EMPTY_TOKEN})
            # assert response.status_code == 422
            # assert response.headers["content-type"] == "application/json"
            # content = response.json()
            # assert content["code"] == "requestParametersInvalid"
            # assert content["title"] == "Request Parameters Invalid"

            # make a call which triggers a bug to trigger a JSON parse error
            # response = client.get("/link", headers={"Authorization": BAD_JSON})
            # assert response.status_code == 502
            # assert response.headers["content-type"] == "application/json"
            # content = response.json()
            # assert content["code"] == "badContentType"
            # assert content["title"] == "Received Incorrect Content Type"

            # make a call which triggers a bug to trigger a JSON parse error
            # this simulates a 500 error in the auth service which emits text
            # rather than JSON - in other words, a deep and actual server error,
            # not the usuall, silly 500 response we emit for all JSON-RPC!!
            response = client.get("/link", headers={"Authorization": TEXT_JSON})
            assert response.status_code == 502
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.json_decode_error.code
            # assert content["title"] == "Error Decoding Response"

            # make a call which triggers a bug to trigger a JSON parse error
            response = client.get(
                "/link", headers={"Authorization": CAUSES_INTERNAL_ERROR}
            )
            assert response.status_code == 500
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.internal_server_error.code
            # assert content["title"] == "Internal Server Error"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case an endpoint not found.
            response = client.post("/linx", headers={"Authorization": "x" * 32})
            assert response.status_code == 404
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.not_found.code
            assert content["title"] == errors.ERRORS.not_found.title
            assert content["message"] == "The requested resource was not found"
            assert content["data"]["detail"] == "Not Found"
            assert content["data"]["path"] == "/linx"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case a method not supported.
            response = client.post("/link", headers={"Authorization": "x" * 32})
            assert response.status_code == 405
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.fastapi_error.code
            assert content["title"] == errors.ERRORS.fastapi_error.title
            assert content["message"] == "Internal FastAPI Exception"
            assert content["data"]["detail"] == "Method Not Allowed"
