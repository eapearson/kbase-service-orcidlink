import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from unittest import mock

import pytest

from orcidlink.lib.auth import ensure_authorization, get_username
from orcidlink.lib.service_clients.kbase_auth import TokenInfo
from orcidlink.lib.utils import module_path


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


@pytest.fixture(name="fake_fs")
def fake_fs_fixture(fs):
    fs.add_real_directory(module_path("test/data"))
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
