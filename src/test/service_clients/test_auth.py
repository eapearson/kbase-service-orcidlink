from test.lib.test_responses import mock_services
from test.mocks.data import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr

import pytest

from orcidlink.lib import utils
from orcidlink.lib.errors import ServiceError
from orcidlink.service_clients import auth
from orcidlink.service_clients.auth import ensure_authorization
from orcidlink.service_clients.KBaseAuth import TokenInfo

config_yaml = load_data_file("config1.toml")


@pytest.fixture(name="fake_fs")
def fake_fs_fixture(fs):
    fs.create_file(utils.module_path("deploy/config.toml"), contents=config_yaml)
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


async def test_auth_get_username(fake_fs):
    with no_stderr():
        with mock_auth_service():
            username = await auth.get_username("foo")
            assert username == "foo"


async def test_ensure_authorization():
    with mock_services():
        authorization, value = await ensure_authorization("foo")
        assert isinstance(authorization, str)
        assert authorization == "foo"
        assert isinstance(value, TokenInfo)

    with pytest.raises(ServiceError, match="API call requires a KBase auth token"):
        await ensure_authorization(None)
