import contextlib
import os
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import (
    create_link,
    generate_kbase_token,
    get_link,
    update_link,
)
from unittest import mock

import pytest

from orcidlink.jsonrpc.errors import NotFoundError
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import LinkRecord
from orcidlink.process import (
    delete_link,
    link_record_for_orcid_id,
    link_record_for_user,
)

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]
TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")

kbase_yaml = load_data_file(TEST_DATA_DIR, "kbase1.yml")

INVALID_TOKEN = generate_kbase_token("invalid_token")
EMPTY_TOKEN = ""
# NO_TOKEN = generate_kbase_token("no_token")
BAD_JSON = generate_kbase_token("bad_json")
TEXT_JSON = generate_kbase_token("text_json")
CAUSES_INTERNAL_ERROR = generate_kbase_token("something_bad")


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


# Happy paths


# Error conditions


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_main_404(fake_fs):
#     response = client.get("/foo")
#     assert response.status_code == 404


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_link():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            # Adds a test link directly to the database
            await create_link(TEST_LINK)

            link_record = await get_link("foo")

            assert isinstance(link_record, LinkRecord)

            await delete_link("foo")

            link_record = await get_link("foo")

            assert link_record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_delete_link_error_not_found():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            # Adds a test link directly to the database
            await create_link(TEST_LINK)

            with pytest.raises(NotFoundError):
                await delete_link("bar")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_user():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_user("foo")
            assert link_record is not None
            assert link_record.username == "foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_user_error_not_found():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_user("bar")
            assert link_record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_user_with_refresh():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_user("foo")
            assert link_record is not None
            assert link_record.username == "foo"

            old_access_token = link_record.orcid_auth.access_token

            link_record.retires_at = posix_time_millis()
            await update_link(link_record)

            new_link_record = await link_record_for_user("foo")

            assert new_link_record is not None

            new_access_token = new_link_record.orcid_auth.access_token

            assert old_access_token != new_access_token


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_orcid_id():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_orcid_id("orcid-id-foo")
            assert link_record is not None
            assert link_record.username == "foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_orcid_id_error_not_found():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_orcid_id("orcid-id-bar")
            assert link_record is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_link_record_for_orcid_id_with_refresh():
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            await create_link(TEST_LINK)

            link_record = await link_record_for_orcid_id("orcid-id-foo")
            assert link_record is not None
            assert link_record.username == "foo"

            old_access_token = link_record.orcid_auth.access_token

            link_record.retires_at = posix_time_millis()
            await update_link(link_record)

            new_link_record = await link_record_for_orcid_id("orcid-id-foo")

            assert new_link_record is not None

            new_access_token = new_link_record.orcid_auth.access_token

            assert old_access_token != new_access_token
