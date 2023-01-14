import contextlib

import pytest
from fastapi.testclient import TestClient
from orcidlink.lib import storage_model
from orcidlink.lib.config import config
from orcidlink.main import app
from orcidlink.model_types import LinkRecord, ORCIDProfile
from orcidlink.routers.orcid import orcid_profile_to_normalized
from test.data.utils import load_data_file, load_data_json, load_test_data
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)

client = TestClient(app)

config_yaml = load_data_file("config1.yaml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


TEST_LINK = load_data_json("link2.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            with mock_orcid_api_service():
                yield


@pytest.fixture(autouse=True)
def around_tests(fake_fs):
    config(True)
    yield


def create_link():
    sm = storage_model.storage_model()
    sm.db.links.drop()
    sm.create_link_record(LinkRecord.parse_obj(TEST_LINK))


#
# Tests
#


def test_router_profile_to_normalized():
    orcid_id = "0000-0003-4997-3076"
    raw_profile = load_test_data("orcid", "profile")
    model_profile = load_test_data("orcid", "profile-model")
    email = load_test_data("orcid", "email")
    assert (
        orcid_profile_to_normalized(orcid_id, raw_profile, email).dict()
        == ORCIDProfile.parse_obj(model_profile).dict()
    )


def test_router_profile_to_normalized_single_affiliation():
    orcid_id = "0000-0003-4997-3076"
    raw_profile = load_test_data("orcid", "profile-single-affiliation")
    model_profile = load_test_data("orcid", "profile-model-single-affiliation")
    email = load_test_data("orcid", "email")
    assert (
        orcid_profile_to_normalized(orcid_id, raw_profile, email).dict()
        == ORCIDProfile.parse_obj(model_profile).dict()
    )


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
        create_link()
        response = TestClient(app).get(
            "/orcid/profile", headers={"Authorization": "foo"}
        )
        assert response.status_code == 200


def test_get_profile_not_found(fake_fs):
    with mock_services():
        response = TestClient(app).get(
            "/orcid/profile", headers={"Authorization": "bar"}
        )
        assert response.status_code == 404
