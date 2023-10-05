import copy
import os
from test.mocks.data import load_data_json
from test.mocks.env import TEST_ENV
from unittest import mock

import pytest

from orcidlink.jsonrpc.errors import NotFoundError
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import LinkingSessionInitial, LinkRecord, ORCIDAuth

# TODO: is it really worth it separately testing the mongo storage model? If so,
# we should not use the generic storage_model!
from orcidlink.storage.storage_model import storage_model


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
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
    "retires_at": 3,
    "orcid_auth": {
        "access_token": "foo",
        "token_type": "bar",
        "refresh_token": "baz",
        "expires_in": 3,
        "scope": "boo",
        "name": "abc",
        "orcid": "def",
    },
}

EXAMPLE_LINK_RECORD_2 = {"session_id": "bar", "username": "foo"}
TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]

EXAMPLE_LINK_RECORD_3 = {
    "session_id": "baz",
    "username": "bar",
    "created_at": 1,
    "expires_at": 2,
    "retires_at": 3,
    "orcid_auth": {
        "access_token": "bar",
        "token_type": "bar",
        "refresh_token": "baz",
        "expires_in": 3,
        "scope": "boo",
        "name": "abc",
        "orcid": "def",
    },
}


EXAMPLE_LINKING_SESSION_COMPLETED_1 = load_data_json(
    TEST_DATA_DIR, "linking_session_record_completed.json"
)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_create_link_record():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_save_link_record():
    sm = storage_model()
    await sm.reset_database()
    link_record = LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1)
    await sm.create_link_record(link_record)

    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    record = await sm.get_link_record_for_orcid_id(link_record.orcid_auth.orcid)
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    updated_record = LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1)
    updated_record.orcid_auth.access_token = "fee"
    await sm.save_link_record(updated_record)
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "fee"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_link_record_for_orcid_id():
    sm = storage_model()
    await sm.reset_database()
    link_record = LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1)
    await sm.create_link_record(link_record)

    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    record = await sm.get_link_record_for_orcid_id(link_record.orcid_auth.orcid)
    assert record is not None
    assert record.orcid_auth.access_token == "foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_link_record_for_orcid_id_not_found():
    sm = storage_model()
    await sm.reset_database()
    link_record = LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1)
    await sm.create_link_record(link_record)

    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    record = await sm.get_link_record_for_orcid_id("baz")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_link_record():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    await sm.delete_link_record("foo")

    record = await sm.get_link_record("foo")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_link_record():
    sm = storage_model()
    await sm.reset_database()

    # Create one link record
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    # Try another one.
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_3))
    record = await sm.get_link_record("bar")
    assert record is not None
    assert record.orcid_auth.access_token == "bar"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_link_records():
    sm = storage_model()
    await sm.reset_database()

    # Create one link record
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    # Try another one.
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_3))
    record = await sm.get_link_record("bar")
    assert record is not None
    assert record.orcid_auth.access_token == "bar"

    # Now ... get them both!

    records = await sm.get_link_records()
    assert record is not None
    assert len(records) == 2


#
# Linking session records
#

EXAMPLE_LINKING_SESSION_RECORD_1 = {
    "session_id": "foo-session",
    "username": "foo",
    "created_at": 123,
    "expires_at": 456,
}


EXAMPLE_LINKING_SESSION_RECORD_2 = {
    "session_id": "bar-session",
    "username": "bar",
    "created_at": 123,
    "expires_at": 456,
}

EXAMPLE_LINKING_SESSION_RECORD_3 = {
    "session_id": "baz-session",
    "username": "baz",
    "created_at": 123,
    "expires_at": 456,
}


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_create_linking_session():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_session_initial_not_found():
    sm = storage_model()
    await sm.reset_database()

    record = await sm.get_linking_session_initial("foo-session")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_session_started_not_found():
    sm = storage_model()
    await sm.reset_database()

    record = await sm.get_linking_session_started("foo-sesssion")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_session_completed_not_found():
    sm = storage_model()
    await sm.reset_database()

    record = await sm.get_linking_session_completed("foo-session")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_sessions_initial():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_2)
    )
    result = await sm.get_linking_sessions_initial()
    assert len(result) == 2


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_sessions_started():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_2)
    )
    result = await sm.get_linking_sessions_started()
    assert len(result) == 0

    # Now move them onto started.
    await sm.update_linking_session_to_started(
        "foo-session", "return-link", False, "ui-options"
    )
    await sm.update_linking_session_to_started(
        "bar-session", "return-link", False, "ui-options"
    )
    result = await sm.get_linking_sessions_started()
    assert len(result) == 2


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_sessions_completed():
    sm = storage_model()
    await sm.reset_database()

    result = await sm.get_linking_sessions_initial()
    assert len(result) == 0
    result = await sm.get_linking_sessions_started()
    assert len(result) == 0
    result = await sm.get_linking_sessions_completed()
    assert len(result) == 0

    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_2)
    )
    result = await sm.get_linking_sessions_initial()
    assert len(result) == 2
    result = await sm.get_linking_sessions_started()
    assert len(result) == 0
    result = await sm.get_linking_sessions_completed()
    assert len(result) == 0

    # Now move them onto started.
    await sm.update_linking_session_to_started(
        "foo-session", "return-link", False, "ui-options"
    )
    await sm.update_linking_session_to_started(
        "bar-session", "return-link", False, "ui-options"
    )
    result = await sm.get_linking_sessions_initial()
    assert len(result) == 0
    result = await sm.get_linking_sessions_started()
    assert len(result) == 2
    result = await sm.get_linking_sessions_completed()
    assert len(result) == 0

    # Now move them onto completed!
    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )
    await sm.update_linking_session_to_finished("foo-session", orcid_auth)

    # Now move them onto completed!
    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )
    await sm.update_linking_session_to_finished("bar-session", orcid_auth)
    result = await sm.get_linking_sessions_initial()
    assert len(result) == 0
    result = await sm.get_linking_sessions_started()
    assert len(result) == 0
    result = await sm.get_linking_sessions_completed()
    assert len(result) == 2


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_linking_sessions_stats_nothing():
    sm = storage_model()
    await sm.reset_database()

    stats = await sm.get_stats()
    assert stats.linking_sessions_initial.active == 0
    assert stats.linking_sessions_initial.expired == 0
    assert stats.linking_sessions_started.active == 0
    assert stats.linking_sessions_started.expired == 0
    assert stats.linking_sessions_completed.active == 0
    assert stats.linking_sessions_completed.expired == 0
    assert stats.links.all_time == 0
    assert stats.links.last_24_hours == 0
    assert stats.links.last_7_days == 0
    assert stats.links.last_30_days == 0


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_save_linking_record():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    await sm.update_linking_session_to_started(
        "foo-session", "return-link", False, "ui-options"
    )
    record2 = await sm.get_linking_session_started("foo-session")
    assert record2 is not None
    assert record2.return_link == "return-link"
    assert record2.skip_prompt is False
    assert record2.ui_options == "ui-options"

    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )

    await sm.update_linking_session_to_finished("foo-session", orcid_auth)
    record3 = await sm.get_linking_session_completed("foo-session")
    assert record3 is not None
    assert record3.orcid_auth.access_token == "a"

    await sm.delete_linking_session_completed("foo-session")

    record = await sm.get_linking_session_completed("foo-session")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_update_linking_session_to_started_bad_session_id():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    with pytest.raises(NotFoundError):
        await sm.update_linking_session_to_started(
            "baz", "return-link", False, "ui-options"
        )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_update_linking_session_to_finished_bad_session_id():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    await sm.update_linking_session_to_started(
        "foo-session", "return-link", False, "ui-options"
    )
    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )

    with pytest.raises(NotFoundError) as error:
        await sm.update_linking_session_to_finished("baz", orcid_auth)

    assert error.value.MESSAGE == "Not Found"
    assert error.value.CODE == NotFoundError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_linking_session_started():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    await sm.update_linking_session_to_started(
        "foo-session", "return-link", False, "ui-options"
    )
    record2 = await sm.get_linking_session_started("foo-session")
    assert record2 is not None
    assert record2.return_link == "return-link"
    assert record2.skip_prompt is False
    assert record2.ui_options == "ui-options"

    await sm.delete_linking_session_started("foo-session")
    record3 = await sm.get_linking_session_started("foo-session")
    assert record3 is None

    # orcid_auth = ORCIDAuth(
    #     access_token="a",
    #     token_type="b",
    #     refresh_token="c",
    #     expires_in=123,
    #     scope="d",
    #     name="e",
    #     orcid="f"
    # )

    # await sm.update_linking_session_to_finished("bar", orcid_auth)
    # record3 = await sm.get_linking_session_completed("bar")
    # assert record3 is not None
    # assert record3.orcid_auth.access_token == "a"

    # await sm.delete_linking_session_completed("bar")

    # record = await sm.get_linking_session_completed("bar")
    # assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_linking_session_initial():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("foo-session")
    assert record is not None
    assert record.session_id == "foo-session"

    await sm.delete_linking_session_initial("foo-session")

    record = await sm.get_linking_session_initial("foo-session")
    assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_expired_sessions():
    sm = storage_model()
    await sm.reset_database()

    now = posix_time_millis()
    # make a time one minute in the past.
    in_the_past = now - 60 * 1000
    test_session_1 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    test_session_1["expires_at"] = in_the_past
    test_session_2 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_2)
    test_session_2["expires_at"] = in_the_past
    test_session_3 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_3)
    test_session_3["expires_at"] = in_the_past

    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_2)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_3)
    )

    # Now move them onto started.
    await sm.update_linking_session_to_started(
        "bar-session", "return-link", False, "ui-options"
    )
    await sm.update_linking_session_to_started(
        "baz-session", "return-link", False, "ui-options"
    )

    # Now move them onto completed!
    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )
    await sm.update_linking_session_to_finished("baz-session", orcid_auth)

    stats = await sm.get_stats()
    assert stats.linking_sessions_initial.active == 0
    assert stats.linking_sessions_initial.expired == 1
    assert stats.linking_sessions_started.active == 0
    assert stats.linking_sessions_started.expired == 1
    assert stats.linking_sessions_completed.active == 0
    assert stats.linking_sessions_completed.expired == 1
    assert stats.links.all_time == 0
    assert stats.links.last_24_hours == 0
    assert stats.links.last_7_days == 0
    assert stats.links.last_30_days == 0

    await sm.delete_expired_sesssions()
    stats = await sm.get_stats()
    assert stats.linking_sessions_initial.expired == 0
    assert stats.linking_sessions_started.expired == 0
    assert stats.linking_sessions_completed.expired == 0


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_expired_sessions():
    sm = storage_model()
    await sm.reset_database()

    now = posix_time_millis()
    # make a time one minute in the past.
    in_the_past = now - 60 * 1000
    test_session_1 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    test_session_1["expires_at"] = in_the_past
    test_session_2 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_2)
    test_session_2["expires_at"] = in_the_past
    test_session_3 = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_3)
    test_session_3["expires_at"] = in_the_past

    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_2)
    )
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_3)
    )

    # Now move them onto started.
    await sm.update_linking_session_to_started(
        "bar-session", "return-link", False, "ui-options"
    )
    await sm.update_linking_session_to_started(
        "baz-session", "return-link", False, "ui-options"
    )

    # Now move them onto completed!
    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
    )
    await sm.update_linking_session_to_finished("baz-session", orcid_auth)

    expired_initial = await sm.get_expired_initial_sessions(now)
    assert len(expired_initial) == 1

    expired_started = await sm.get_expired_started_sessions(now)
    assert len(expired_started) == 1

    expired_completed = await sm.get_expired_completed_sessions(now)
    assert len(expired_completed) == 1

    expired_sessions = await sm.get_expired_sessions(now)
    assert len(expired_sessions.initial_sessions) == 1
    assert len(expired_sessions.started_sessions) == 1
    assert len(expired_sessions.completed_sessions) == 1
