import os
from test.mocks.data import load_data_file
from test.mocks.env import TEST_ENV
from test.mocks.testing_utils import assert_json_rpc_error
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from orcidlink.jsonrpc.methods.error_info import ErrorInfoResult, error_info_method
from orcidlink.main import app
from orcidlink.runtime import service_path

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]


client = TestClient(app, raise_server_exceptions=False)

service_description_toml = load_data_file(TEST_DATA_DIR, "service_description1.toml")
git_info_json = load_data_file(TEST_DATA_DIR, "git_info1.json")


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        fs.create_file(
            service_path("SERVICE_DESCRIPTION.toml"), contents=service_description_toml
        )
        fs.create_file(service_path("build/git-info.json"), contents=git_info_json)
        fs.add_real_directory(data_dir)
        yield fs


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_error_info_method(fake_fs):
    result = error_info_method(1010)
    assert isinstance(result, ErrorInfoResult)

    assert result.error_info.code == 1010


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_call_info(fake_fs):
    rpc = {
        "jsonrpc": "2.0",
        "id": "123",
        "method": "error-info",
        "params": {"error_code": 1010},
    }
    response = client.post("/api/v1", json=rpc)
    assert response.status_code == 200
    json_response = response.json()
    assert "result" in json_response
    result = json_response["result"]

    assert "error_info" in result
    error_info = result["error_info"]
    assert "code" in error_info
    assert error_info["code"] == 1010


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_call_info_error_code_not_found(fake_fs):
    rpc = {
        "jsonrpc": "2.0",
        "id": "123",
        "method": "error-info",
        "params": {"error_code": 666},
    }
    response = client.post("/api/v1", json=rpc)
    assert response.status_code == 200
    assert_json_rpc_error(response, 1020, "Not Found")
