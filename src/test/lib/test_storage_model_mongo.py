import pytest
from orcidlink.lib.config import config
from orcidlink.lib.storage_model import storage_model
from orcidlink.model_types import LinkRecord, LinkingSessionInitial, ORCIDAuth


@pytest.fixture
def my_fs(fs):
    fake_config = """
kbase:
  services:
    Auth2:
      url: https://ci.kbase.us/services/auth/api/V2/token
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
module:
  CLIENT_ID: 'REDACTED-CLIENT-ID'
  CLIENT_SECRET: 'REDACTED-CLIENT-SECRET'
  IS_DYNAMIC_SERVICE: 'yes'
  MONGO_USERNAME: 'dev'
  MONGO_PASSWORD: 'd3v'
  STORAGE_MODEL: 'mongo'
    """
    fs.create_file("/kb/module/config/config.yaml", contents=fake_config)
    yield fs


def test_constructor():
    model = storage_model()
    assert model is not None


#
# User records
#

EXAMPLE_LINK_RECORD_1 = {
    "session_id": "bar",
    "username": "foo",
    "created_at": 1,
    "expires_at": 2,
    "orcid_auth": {
        "access_token": "foo",
        "token_type": "bar",
        "refresh_token": "baz",
        "expires_in": 3,
        "scope": "boo",
        "name": "abc",
        "orcid": "def",
        "id_token": "xyz"
    }
}

EXAMPLE_LINK_RECORD_2 = {
    "session_id": "bar",
    "username": "foo"
}


@pytest.fixture(autouse=True)
def around_tests(my_fs):
    config(True)
    yield


def test_create_link_record(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_link_record(LinkRecord.parse_obj(EXAMPLE_LINK_RECORD_1))
    record = sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"


def test_save_link_record(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_link_record(LinkRecord.parse_obj(EXAMPLE_LINK_RECORD_1))
    record = sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    updated_record = LinkRecord.parse_obj(EXAMPLE_LINK_RECORD_1)
    updated_record.orcid_auth.access_token = "fee"
    sm.save_link_record(updated_record)
    record = sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "fee"


def test_delete_link_record(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_link_record(LinkRecord.parse_obj(EXAMPLE_LINK_RECORD_1))
    record = sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    sm.delete_link_record("foo")

    record = sm.get_link_record("foo")
    assert record is None


#
# LInking session records
#

EXAMPLE_LINKING_SESSION_RECORD_1 = {
    "session_id": "bar",
    "username": "foo",
    "created_at": 123,
    "expires_at": 456
}


def test_create_linking_session(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_linking_session(LinkingSessionInitial.parse_obj(EXAMPLE_LINKING_SESSION_RECORD_1))
    record = sm.get_linking_session("bar")
    assert record is not None
    assert record.session_id == "bar"


def test_save_linking_record(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_linking_session(LinkingSessionInitial.parse_obj(EXAMPLE_LINKING_SESSION_RECORD_1))
    record = sm.get_linking_session("bar")
    assert record is not None
    assert record.session_id == "bar"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    sm.update_linking_session_to_started("bar", "return-link", "skip-prompt")
    record2 = sm.get_linking_session("bar")
    assert record2 is not None
    assert record2.return_link == "return-link"
    assert record2.skip_prompt == "skip-prompt"

    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
        id_token="g"
    )

    sm.update_linking_session_to_finished("bar", orcid_auth)
    record3 = sm.get_linking_session("bar")
    assert record3 is not None
    assert record3.orcid_auth.access_token == "a"


def test_delete_linking_record(my_fs):
    sm = storage_model()
    sm.reset_database()
    sm.create_linking_session(LinkingSessionInitial.parse_obj(EXAMPLE_LINKING_SESSION_RECORD_1))
    record = sm.get_linking_session("bar")
    assert record is not None
    assert record.session_id == "bar"

    sm.delete_linking_session("bar")

    record = sm.get_linking_session("bar")
    assert record is None
