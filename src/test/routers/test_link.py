import contextlib
import os

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from test.mocks.mock_contexts import mock_auth_service, mock_orcid_oauth_service, no_stderr

client = TestClient(app)


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
    serviceRequestTimeout: 60000
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
    yield fs


# def no_std_err():
#     with contextlib.redirect_stderr(open(os.devnull, "w")) as c1:
#         yield

@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            yield


#
# Tests
#

def test_get_link(fake_fs):
    with mock_services():
        client = TestClient(app)
        response = client.get("/link",
                              headers={"Authorization": "foo"})
        assert response.status_code == 200

        response = client.get("/link",
                              headers={"Authorization": "foox"})
        assert response.status_code == 401

        response = client.get("/link",
                              headers={"Authorization": "bar"})
        assert response.status_code == 404


def test_is_linked(fake_fs):
    with mock_services():
        client = TestClient(app)
        response = client.get("/link/is_linked",
                              headers={"Authorization": "foo"})
        result = response.json()
        assert result is True

        response = client.get("/link/is_linked",
                              headers={"Authorization": "bar"})
        result = response.json()
        assert result is False

        response = client.get("/link/is_linked",
                              headers={"Authorization": "baz"})
        assert response.status_code == 401


def test_delete_link(fake_fs):
    with contextlib.redirect_stderr(open(os.devnull, "w")):
        with mock_auth_service():
            with mock_orcid_oauth_service():
                client = TestClient(app)
                # client.headers['authorization'] = 'foo'

                response = client.delete("/link",
                                         headers={"Authorization": "foo"})
                assert response.status_code == 204

                response = client.delete("/link",
                                         headers={"Authorization": "bar"})
                assert response.status_code == 204
