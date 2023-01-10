from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from test.mocks.mock_contexts import mock_auth_service, no_stderr

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def fake_fs(fs):
    fake_config = """
kbase:
  services:
    Auth2:
      url: http://127.0.0.1:9999/services/auth/api/V2/token
      tokenCacheLifetime: 300000
      tokenCacheMaxSize: 20000
    ServiceWizard:
      url: http://127.0.0.1:9999/services/service_wizard
  uiOrigin: https://ci.kbase.us
  defaults:
    serviceRequestTimeout: 500
orcid:
  oauthBaseURL: https://sandbox.orcid.org/oauth
  baseURL: https://sandbox.orcid.org
  apiBaseURL: https://api.sandbox.orcid.org/v3.0
env:
  CLIENT_ID: 'REDACTED-CLIENT-ID'
  CLIENT_SECRET: 'REDACTED-CLIENT-SECRET'
  IS_DYNAMIC_SERVICE: 'yes'
    """
    fs.create_file("/kb/module/config/config.yaml", contents=fake_config)

    fake_index = """
    {
    "last_id": 9,
    "entities": {
        "foo": {
            "id": 9,
            "metadata": {},
            "events": [
                {
                    "event": "created",
                    "at": "2022-12-02T01:13:36.533017+00:00"
                }
            ]
        }
    }
}
    """
    fs.create_file("/kb/module/work/data/users/index.json", contents=fake_index)

    fake_link_record = """
    {
    "orcid_auth": {
        "access_token": "1eef6e01-62be-467c-b140-973011ef0cb7",
        "token_type": "bearer",
        "refresh_token": "0111ac66-c9a8-42ef-9e71-109ae091b8df",
        "expires_in": 631138518,
        "scope": "/read-limited openid /activities/update",
        "name": "Erik Pearson",
        "orcid": "0000-0003-4997-3076",
        "id_token": "eyJraWQiOiJzYW5kYm94LW9yY2lkLW9yZy0zaHBnb3NsM2I2bGFwZW5oMWV3c2dkb2IzZmF3ZXBvaiIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiRGsyR01qZ1FTdVYwZFJ5SUZMYmd3dyIsImF1ZCI6IkFQUC1SQzNQTTNLU01NVjNHS1dTIiwic3ViIjoiMDAwMC0wMDAzLTQ5OTctMzA3NiIsImF1dGhfdGltZSI6MTY2OTk0MzYxMiwiYW1yIjoicHdkIiwiaXNzIjoiaHR0cHM6XC9cL3NhbmRib3gub3JjaWQub3JnIiwiZXhwIjoxNjcwMDMwMDE0LCJnaXZlbl9uYW1lIjoiRXJpayIsImlhdCI6MTY2OTk0MzYxNCwiZmFtaWx5X25hbWUiOiJQZWFyc29uIiwianRpIjoiMjU3Y2U3MjItMzZhYS00ZjJjLTllN2YtMDJlZWEzZGIzZDk2In0.mMIWYtPCq52YQYugff57tejpZhnL_8J9_eARgd-niVHtA-lFnrVGaoL-oVzr5gqjWFvCuAyZU78pKxFaSczcwDViW2UeBmgFjFyj0hokmoXc6iH51XQUc_X3hwCod67oY8dyMPMy_awAIgUQ3ZK3Se64Pd1_odoLZi4O7oSba5dMnQ2tD0s-57BcPfittp6vqXVGE00K1M-qyrR72Lmj6ML2xfORPfUOZW6M3zLyX_ipBE36tQk1cjQhveNwUgDFlsiA1p6V1s1L7vpIiNpB1y9lOmUZQJICnusKMQ35EHPtS7saybwvXH7EwqwN9kvMfEOekbwHgYvsPrAbHHh06g"
    },
    "created_at": 1669943616532,
    "expires_at": 2301082134532
}
    """
    fs.create_file("/kb/module/work/data/users/9.json", contents=fake_link_record)

    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


# Happy paths

def test_main_status():
    response = client.get("/status")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response['status'] == "ok"
    assert isinstance(json_response['time'], str)
    status_time = datetime.fromisoformat(json_response['time'])
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - status_time
    assert abs(time_diff.total_seconds()) < 1


def test_main_info():
    response = client.get("/info")
    assert response.status_code == 200


def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200


# Error conditions

def test_main_404():
    response = client.get("/foo")
    assert response.status_code == 404


def test_validation_exception_handler():
    response = client.post("/works", json={
        "foo": "bar"
    })
    assert response.status_code == 422
    assert response.headers['content-type'] == 'application/json'
    content = response.json()
    assert content['code'] == 'requestParametersInvalid'
    assert content['title'] == "Request Parameters Invalid"
    assert content['message'] == "This request does not comply with the schema for this endpoint"


def test_kbase_auth_exception_handler(fs):
    with no_stderr():
        with mock_auth_service() as [_, _, url]:
            # call with missing token
            response = client.get("/link",
                                  headers={
                                  })
            assert response.status_code == 401
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'missingToken'
            assert content['title'] == "Missing Token"
            assert content['message'] == "API call requires a KBase auth token"

            # call with invalid token
            response = client.get("/link",
                                  headers={
                                      'Authorization': 'baz'
                                  })
            assert response.status_code == 401
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'invalidToken'
            assert content['title'] == "KBase auth token is invalid"

            # make a call which triggers a bug to trigger a JSON parse error
            response = client.get("/link",
                                  headers={
                                      'Authorization': 'bad_json'
                                  })
            assert response.status_code == 500
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'authError'
            assert content['title'] == "Unknown error authenticating with KBase"

            # make a call which triggers a bug to trigger a JSON parse error
            response = client.get("/link",
                                  headers={
                                      'Authorization': 'something_bad'
                                  })
            assert response.status_code == 500
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'internalServerError'
            assert content['title'] == "Internal Server Error"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case a method not supported.
            response = client.post("/linx",
                                   headers={
                                       'Authorization': 'internal_server_error'
                                   })
            assert response.status_code == 404
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'notFound'
            assert content['title'] == "Not Found"
            assert content['message'] == "The requested resource was not found"
            assert content['data']['detail'] == 'Not Found'
            assert content['data']['path'] == '/linx'

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case a method not supported.
            response = client.post("/link",
                                   headers={
                                       'Authorization': 'internal_server_error'
                                   })
            assert response.status_code == 405
            assert response.headers['content-type'] == 'application/json'
            content = response.json()
            assert content['code'] == 'fastapiError'
            assert content['title'] == "FastAPI Error"
            assert content['message'] == "Internal FastAPI Exception"
            assert content['data']['detail'] == 'Method Not Allowed'
