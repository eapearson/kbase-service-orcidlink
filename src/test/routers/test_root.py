from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from test.data.utils import load_data_file, load_data_json

client = TestClient(app, raise_server_exceptions=False)

config_yaml = load_data_file("config1.toml")
service_description_toml = load_data_file("service_description1.toml")
gitinfo_toml = load_data_file("git_info1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.toml", contents=config_yaml)
    fs.create_file(
        "/kb/module/SERVICE_DESCRIPTION.toml", contents=service_description_toml
    )
    fs.create_file("/kb/module/config/git-info.toml", contents=gitinfo_toml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


TEST_LINK = load_data_json("link1.json")


# Happy paths


def test_main_status(fake_fs):
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert isinstance(json_response["time"], int)
    assert isinstance(json_response["start_time"], int)
    status_time = datetime.fromtimestamp(json_response["time"] / 1000, tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - status_time
    assert abs(time_diff.total_seconds()) < 1


def test_main_info(fake_fs):
    response = client.get("/info")
    assert response.status_code == 200
    result = response.json()
    service_description = result["service-description"]
    assert "module-name" in service_description
    assert service_description["module-name"] == "ORCIDLink"
    git_info = result["git-info"]
    assert git_info["author_name"] == "Foo Bar"
