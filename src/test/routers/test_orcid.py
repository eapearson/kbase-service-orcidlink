import contextlib

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from orcidlink.model_types import ORCIDProfile
from orcidlink.routers.orcid import orcid_profile_to_normalized
from test.data.utils import load_test_data
from test.mocks.mock_contexts import mock_auth_service, mock_orcid_api_service, no_stderr

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

    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            with mock_orcid_api_service():
                yield


#
# Tests
#

def test_router_profile_to_normalized():
    orcid_id = '0000-0003-4997-3076'
    raw_profile = load_test_data('orcid', 'profile')
    model_profile = load_test_data('orcid', 'profile-model')
    email = load_test_data('orcid', 'email')
    assert orcid_profile_to_normalized(orcid_id, raw_profile, email).dict() == ORCIDProfile.parse_obj(
        model_profile).dict()


def test_router_profile_to_normalized_single_affiliation():
    orcid_id = '0000-0003-4997-3076'
    raw_profile = load_test_data('orcid', 'profile-single-affiliation')
    model_profile = load_test_data('orcid', 'profile-model-single-affiliation')
    email = load_test_data('orcid', 'email')
    assert orcid_profile_to_normalized(orcid_id, raw_profile, email).dict() == ORCIDProfile.parse_obj(
        model_profile).dict()


# def test_get_profile():
#     server = MockServer("127.0.0.1", MockORCIDOAuth2)
#     server.start_service()
#     try:
#         client = ORCIDOAuthClient(
#             url=server.base_url(),
#             access_token="access_token"
#         )
#         with pytest.raises(ErrorException, match="Error fetching data from ORCID Auth api"):
#             client.revoke_token()
#     except Exception as ex:
#         pytest.fail(f"Unexpected exception raised: {str(ex)}")
#     finally:
#         server.stop_service()


def test_get_profile(fake_fs):
    with mock_services():
        response = TestClient(app).get("/orcid/profile",
                                       headers={"Authorization": "foo"}
                                       )
        assert response.status_code == 200


def test_get_profile_not_found(fake_fs):
    with mock_services():
        response = TestClient(app).get("/orcid/profile",
                                       headers={"Authorization": "bar"}
                                       )
        assert response.status_code == 404
