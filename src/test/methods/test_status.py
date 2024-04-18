import os
from datetime import datetime, timezone
from test.mocks.env import TEST_ENV
from unittest import mock

from fastapi.testclient import TestClient

from orcidlink.jsonrpc.methods.status import StatusResult, status_method
from orcidlink.main import app

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]


client = TestClient(app, raise_server_exceptions=False)

# Happy paths


def test_status_method():
    result = status_method()
    assert isinstance(result, StatusResult)
    assert result.status == "ok"

    current_time = datetime.fromtimestamp(result.current_time / 1000, tz=timezone.utc)
    now_time = datetime.now(timezone.utc)
    time_diff = now_time - current_time
    assert abs(time_diff.total_seconds()) < 1


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_status():
    rpc = {"jsonrpc": "2.0", "id": "123", "method": "status"}
    response = client.post("/api/v1", json=rpc)
    assert response.status_code == 200
    # assert_json_rpc_result(response, )
    json_response = response.json()
    assert "result" in json_response
    result = json_response["result"]
    assert result["status"] == "ok"
    assert isinstance(result["current_time"], int)
    assert isinstance(result["start_time"], int)
    status_time = datetime.fromtimestamp(result["current_time"] / 1000, tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - status_time
    assert abs(time_diff.total_seconds()) < 1
