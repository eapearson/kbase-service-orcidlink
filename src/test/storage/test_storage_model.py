import os
from test.mocks.data import load_data_json
from test.mocks.env import TEST_ENV
from unittest import mock

import pytest

from orcidlink.lib import utils
from orcidlink.model import LinkingSessionInitial, LinkRecord, ORCIDAuth
from orcidlink.storage.storage_model import storage_model
from orcidlink.storage.storage_model_mongo import StorageModelMongo


@pytest.fixture
def fake_fs(fs):
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_constructor():
    sm = storage_model()
    assert sm is not None

    # And it should be the storage model that fits
    # the configuration, which our tests assume to
    # be 'mongo'.
    assert isinstance(sm, StorageModelMongo)


# TODO: test constructor errors when config is bad
#
# def test_constructor_errors(temp_config):
#     with pytest.raises(ValueError) as ve:
#         temp_config.module.STORAGE_MODEL = "foo"
#         storage_model()
#     assert str(ve.value) == 'Unsupported storage model "foo"'


#
# User records
#

EXAMPLE_LINK_RECORD_1 = load_data_json("link3.json")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_create_link_record(fake_fs):
    sm = storage_model()
    await sm.reset_database()
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_save_link_record(fake_fs):
    sm = storage_model()
    await sm.reset_database()
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    updated_record = LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1)
    updated_record.orcid_auth.access_token = "fee"
    await sm.save_link_record(updated_record)
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "fee"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_link_record(fake_fs):
    sm = storage_model()
    await sm.reset_database()
    await sm.create_link_record(LinkRecord.model_validate(EXAMPLE_LINK_RECORD_1))
    record = await sm.get_link_record("foo")
    assert record is not None
    assert record.orcid_auth.access_token == "foo"

    await sm.delete_link_record("foo")

    record = await sm.get_link_record("foo")
    assert record is None


#
# LInking session records
#

EXAMPLE_LINKING_SESSION_RECORD_1 = load_data_json("linking_session_record_initial.json")
EXAMPLE_LINKING_SESSION_COMPLETED_1 = load_data_json(
    "linking_session_record_completed.json"
)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_create_linking_session(fake_fs):
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("bar")
    assert record is not None
    assert record.session_id == "bar"


# def test_save_linking_record(fake_fs):
#     sm = storage_model()
#     sm.reset_database()
#     sm.create_linking_session(
#         LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
#     )
#     record = sm.get_linking_session_initial("bar")
#     assert record is not None
#     assert record.session_id == "bar"

#     # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
#     sm.update_linking_session_to_started("bar", "return-link", "skip-prompt")
#     record2 = sm.get_linking_session_started("bar")
#     assert record2 is not None
#     assert record2.return_link == "return-link"
#     assert record2.skip_prompt == "skip-prompt"

#     orcid_auth = ORCIDAuth(
#         access_token="a",
#         token_type="b",
#         refresh_token="c",
#         expires_in=123,
#         scope="d",
#         name="e",
#         orcid="f",
#         id_token="g",
#     )

#     sm.update_linking_session_to_finished("bar", orcid_auth)
#     record3 = sm.get_linking_session_completed("bar")
#     assert record3 is not None
#     assert record3.orcid_auth.access_token == "a"


# def test_delete_linking_record(fake_fs):
#     sm = storage_model()
#     sm.reset_database()
#     sm.create_linking_session(
#         LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_COMPLETED_1)
#     )
#     record = sm.get_linking_session_completed("bar")
#     assert record is not None
#     assert record.session_id == "bar"

#     sm.delete_linking_session("bar")

#     record = sm.get_linking_session_completed("bar")
#     assert record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_save_linking_record():
    sm = storage_model()
    await sm.reset_database()
    await sm.create_linking_session(
        LinkingSessionInitial.model_validate(EXAMPLE_LINKING_SESSION_RECORD_1)
    )
    record = await sm.get_linking_session_initial("bar")
    assert record is not None
    assert record.session_id == "bar"

    # updated_record = copy.deepcopy(EXAMPLE_LINKING_SESSION_RECORD_1)
    await sm.update_linking_session_to_started(
        "bar", "return-link", False, "ui-options"
    )
    record2 = await sm.get_linking_session_started("bar")
    assert record2 is not None
    assert record2.return_link == "return-link"
    assert record2.skip_prompt == False
    assert record2.ui_options == "ui-options"

    orcid_auth = ORCIDAuth(
        access_token="a",
        token_type="b",
        refresh_token="c",
        expires_in=123,
        scope="d",
        name="e",
        orcid="f",
        id_token="g",
    )

    await sm.update_linking_session_to_finished("bar", orcid_auth)
    record3 = await sm.get_linking_session_completed("bar")
    assert record3 is not None
    assert record3.orcid_auth.access_token == "a"

    await sm.delete_linking_session("bar")

    record = await sm.get_linking_session_completed("bar")
    assert record is None
