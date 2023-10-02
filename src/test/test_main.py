import json
import logging
import os
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from test.mocks.testing_utils import assert_json_rpc_error, generate_kbase_token
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from orcidlink.lib import errors
from orcidlink.lib.logger import log_event
from orcidlink.main import app, config_to_log_level

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]


client = TestClient(app, raise_server_exceptions=False)

kbase_yaml = load_data_file(TEST_DATA_DIR, "kbase1.yml")

INVALID_TOKEN = generate_kbase_token("invalid_token")
EMPTY_TOKEN = ""
# NO_TOKEN = generate_kbase_token("no_token")
BAD_JSON = generate_kbase_token("bad_json")
TEXT_JSON = generate_kbase_token("text_json")
CAUSES_INTERNAL_ERROR = generate_kbase_token("something_bad")


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")


# Happy paths


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_startup(fake_fs):
    with TestClient(app, raise_server_exceptions=False):
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


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_validation_exception_handler(fake_fs):
#     response = client.get("/doc", json={"foo": "bar"})
#     assert response.status_code == 422
#     assert response.headers["content-type"] == "application/json"
#     content = response.json()
#     assert content["code"] == errors.ERRORS.request_validation_error.code
#     assert content["title"] == errors.ERRORS.request_validation_error.title
#     assert (
#         content["message"]
#         == "This request does not comply with the schema for this endpoint"
#     )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_bad_method_call(fake_fs):
    """
    A poorly formed JSON-RPC call should result in a specific error response
    as tested below.
    """
    response = client.post("/api/v1", json={"foo": "bar"})
    assert_json_rpc_error(response, -32600, "Invalid Request")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_bad_params(fake_fs):
    """
    A poorly formed JSON-RPC call should result in a specific error response
    as tested below.
    """
    rpc = {
        "jsonrpc": "2.0",
        "id": "123",
        "method": "get-link",
        "params": {"bar": "foo"},
    }
    response = client.post("/api/v1", json=rpc)
    assert_json_rpc_error(response, -32602, "Invalid params")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_kbase_auth_exception_handler(fake_fs):
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT) as [_, _, url, port]:
            # call with missing token
            rpc = {
                "jsonrpc": "2.0",
                "id": "123",
                "method": "get-link",
                "params": {"username": "foo"},
            }
            response = client.post("/api/v1", json=rpc, headers={})
            assert_json_rpc_error(response, 1010, "Authorization Required")

            # call with invalid token
            response = client.post(
                "/api/v1", json=rpc, headers={"Authorization": INVALID_TOKEN}
            )
            assert_json_rpc_error(response, 1010, "Authorization Required")

            # Call with actual empty token; should be caught at the validator boundary
            # as it is invalid according to the rules for tokens.
            response = client.post("/api/v1", json=rpc, headers={"Authorization": ""})
            assert_json_rpc_error(response, -32602, "Invalid params")

            # make a call which triggers a bug to trigger a JSON parse error
            # this simulates a 500 error in the auth service which emits text
            # rather than JSON - in other words, a deep and actual server error,
            # not the usuall, silly 500 response we emit for all JSON-RPC!!
            response = client.post(
                "/api/v1", json=rpc, headers={"Authorization": TEXT_JSON}
            )
            assert_json_rpc_error(response, 1040, "Error Decoding Response")

            # make some call which triggers a non-404 error caught by FastAPI/Starlette,
            # in this case an endpoint not found.
            response = client.get("/linx", headers={"Authorization": "x" * 32})

            assert response.status_code == 404
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            #
            # TODO: We should make these JSON-RPC!
            #
            assert content["code"] == errors.ERRORS.not_found.code
            assert content["title"] == errors.ERRORS.not_found.title
            assert content["message"] == "The requested resource was not found"
            assert content["data"]["detail"] == "Not Found"
            assert content["data"]["path"] == "/linx"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette,
            # in this case a method not supported.
            response = client.get("/api/v1", headers={"Authorization": "x" * 32})
            assert response.status_code == 405
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == errors.ERRORS.fastapi_error.code
            assert content["title"] == errors.ERRORS.fastapi_error.title
            assert content["message"] == "Internal FastAPI Exception"
            assert content["data"]["detail"] == "Method Not Allowed"


def test_config_to_log_level():
    assert config_to_log_level("DEBUG") == logging.DEBUG
    assert config_to_log_level("INFO") == logging.INFO
    assert config_to_log_level("WARNING") == logging.WARNING
    assert config_to_log_level("ERROR") == logging.ERROR
    assert config_to_log_level("CRITICAL") == logging.CRITICAL


def test_config_to_log_level_error():
    with pytest.raises(ValueError, match='Invalid log_level config setting "FOO"'):
        config_to_log_level("FOO")
