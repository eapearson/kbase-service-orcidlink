import os
from datetime import datetime, timezone
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import TEST_ENV
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from orcidlink.lib import utils
from orcidlink.main import app

client = TestClient(app, raise_server_exceptions=False)

service_description_toml = load_data_file("service_description1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file(
        utils.module_path("SERVICE_DESCRIPTION.toml"), contents=service_description_toml
    )
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


TEST_LINK = load_data_json("link1.json")


# Happy paths


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_main_status(fake_fs):
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert isinstance(json_response["current_time"], int)
    assert isinstance(json_response["start_time"], int)
    status_time = datetime.fromtimestamp(
        json_response["current_time"] / 1000, tz=timezone.utc
    )
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - status_time
    assert abs(time_diff.total_seconds()) < 1


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_main_info(fake_fs):
#     response = client.get("/info")
#     assert response.status_code == 200
#     result = response.json()
#     service_description = result["service-description"]
#     assert "name" in service_description
#     assert service_description["name"] == "ORCIDLink"
#     git_info = result["git-info"]
#     assert git_info["author_name"] == "Foo Bar"
