import pytest
from orcidlink.lib.errors import ServiceError
from orcidlink.service_clients import auth
from orcidlink.service_clients.KBaseAuth import TokenInfo
from orcidlink.service_clients.auth import ensure_authorization
from test.data.utils import load_data_file
from test.lib.test_responses import mock_services
from test.mocks.mock_contexts import mock_auth_service, no_stderr

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_auth_get_username(fake_fs):
    with no_stderr():
        with mock_auth_service():
            assert auth.get_username("foo") == "foo"


def test_ensure_authorization():
    with mock_services():
        authorization, value = ensure_authorization("foo")
        assert isinstance(authorization, str)
        assert authorization == "foo"
        assert isinstance(value, TokenInfo)

    with pytest.raises(
        ServiceError, match="API call requires a KBase auth token"
    ) as ex:
        ensure_authorization(None)
