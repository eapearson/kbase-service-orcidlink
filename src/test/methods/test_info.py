import os
from test.mocks.data import load_data_file
from test.mocks.env import TEST_ENV
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from orcidlink.jsonrpc.methods.info import InfoResult, info_method
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
def test_info_method(fake_fs):
    result = info_method()
    assert isinstance(result, InfoResult)

    assert result.service_description.name == "ORCIDLink"
    assert result.git_info.author_name == "Foo Bar"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_call_info(fake_fs):
    rpc = {"jsonrpc": "2.0", "id": "123", "method": "info"}
    response = client.post("/api/v1", json=rpc)
    assert response.status_code == 200
    json_response = response.json()
    assert "result" in json_response
    result = json_response["result"]

    service_description = result["service-description"]
    assert "name" in service_description
    assert service_description["name"] == "ORCIDLink"
    git_info = result["git-info"]
    assert git_info["author_name"] == "Foo Bar"
