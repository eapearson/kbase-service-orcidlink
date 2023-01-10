import copy

import pytest
from orcidlink.lib.storage_model import StorageModel


@pytest.fixture
def my_data_dir(fs):
    yield fs


def test_constructor():
    fs = StorageModel()
    assert fs is not None


#
# User records
#

EXAMPLE_LINK_RECORD_1 = {
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


def test_create_user_record(my_data_dir):
    sm = StorageModel()
    sm.create_user_record("foo", EXAMPLE_LINK_RECORD_1)
    record = sm.get_user_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"


def test_save_user_record(my_data_dir):
    sm = StorageModel()
    sm.create_user_record("foo", EXAMPLE_LINK_RECORD_1)
    record = sm.get_user_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    updated_record = copy.deepcopy(EXAMPLE_LINK_RECORD_1)
    updated_record["orcid_auth"]["access_token"] = "fee"
    sm.save_user_record("foo", updated_record)
    record = sm.get_user_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "fee"


def test_remove_user_record(my_data_dir):
    sm = StorageModel()
    sm.create_user_record("foo", EXAMPLE_LINK_RECORD_1)
    record = sm.get_user_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    sm.remove_user_record("foo")

    record = sm.get_user_record("foo")
    assert record is None


#
# LInking session records
#

EXAMPLE_LINKING_SESSION_RECORD_1 = {
    "session_id": "foo",
    "username": "bar",
    "created_at": 123,
    "expires_at": 456
}


def test_create_linking_session(my_data_dir):
    sm = StorageModel()
    sm.create_linking_session("foo", EXAMPLE_LINKING_SESSION_RECORD_1)
    record = sm.get_linking_session("foo")
    assert record is not None
    assert record["session_id"] == "foo"


def test_save_linking_record(my_data_dir):
    sm = StorageModel()
    sm.create_linking_session("foo", EXAMPLE_LINKING_SESSION_RECORD_1)
    record = sm.get_linking_session("foo")
    assert record is not None
    assert record["session_id"] == "foo"

    updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    updated_record["session_id"] = "fee"
    sm.update_linking_session("foo", updated_record)
    record = sm.get_linking_session("foo")
    assert record is not None
    assert record["session_id"] == "fee"


def test_remove_linking_record(my_data_dir):
    sm = StorageModel()
    sm.create_linking_session("foo", EXAMPLE_LINKING_SESSION_RECORD_1)
    record = sm.get_linking_session("foo")
    assert record is not None
    assert record["session_id"] == "foo"

    sm.delete_linking_session("foo")

    record = sm.get_linking_session("foo")
    assert record is None
