# from test.lib.test_responses import mock_services
from test.mocks.data import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr
import contextlib
import pytest

from orcidlink.lib.utils import module_path
from orcidlink.lib.errors import ServiceError
from orcidlink.lib.auth import get_username, ensure_authorization
from orcidlink.lib.auth import ensure_authorization
from orcidlink.lib.service_clients.kbase_auth import TokenInfo
import os
from unittest import mock

# config_yaml = load_data_file("config1.toml")

MOCK_KBASE_SERVICES_PORT = 9999
MOCK_ORCID_API_PORT = 9997
MOCK_ORCID_OAUTH_PORT = 9997


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


@pytest.fixture(name="fake_fs")
def fake_fs_fixture(fs):
    # fs.create_file(module_path("deploy/config.toml"), contents=config_yaml)
    fs.add_real_directory(module_path("test/data"))
    yield fs


TEST_ENV = {
    "KBASE_ENDPOINT": f"http://127.0.0.1:{MOCK_KBASE_SERVICES_PORT}/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "MONGO_HOST": "mongo",
    "MONGO_PORT": "27017",
    "MONGO_DATABASE": "orcidlink",
    "MONGO_USERNAME": "dev",
    "MONGO_PASSWORD": "d3v",
    "ORCID_API_BASE_URL": f"http://127.0.0.1:{MOCK_ORCID_API_PORT}",
    "ORCID_OAUTH_BASE_URL": f"http://127.0.0.1:{MOCK_ORCID_OAUTH_PORT}",
}


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
