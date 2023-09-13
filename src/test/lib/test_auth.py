import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from unittest import mock

import pytest

from orcidlink.lib.auth import ensure_account, ensure_authorization, get_username
from orcidlink.lib.service_clients.kbase_auth import AccountInfo, TokenInfo


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


@pytest.fixture(name="fake_fs")
def fake_fs_fixture(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


async def test_auth_get_username(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            username = await get_username("foo")
            assert username == "foo"


async def test_ensure_authorization():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            authorization, value = await ensure_authorization("foo")
            assert isinstance(authorization, str)
            assert authorization == "foo"
            assert isinstance(value, TokenInfo)

        with pytest.raises(Exception, match="Authorization required"):
            await ensure_authorization(None)

        with pytest.raises(Exception, match="Authorization required"):
            await ensure_authorization("")


async def test_ensure_account():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            authorization, account_info = await ensure_account("foo")
            assert isinstance(authorization, str)
            assert authorization == "foo"
            assert isinstance(account_info, AccountInfo)

        with pytest.raises(Exception, match="Authorization required but missing"):
            await ensure_account(None)

        with pytest.raises(Exception, match="Authorization required but missing"):
            await ensure_account("")
