import contextlib

import pytest
from orcidlink.lib import utils
from orcidlink.lib.errors import ServiceError
from orcidlink.service_clients.KBaseAuth import (
    KBaseAuth,
    KBaseAuthError,
    TokenInfo,
)
from test.mocks.data import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file(utils.module_path("deploy/config.toml"), contents=config_yaml)
    yield fs


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service() as [_, _, url]:
            yield url


#
# Auth Client
#


def test_KBaseAuth_constructor_minimal(fake_fs):
    client = KBaseAuth(url="foo", cache_max_size=1, cache_lifetime=1)
    assert client is not None


def test_KBaseAuth_constructor_parameter_errors(fake_fs):
    with pytest.raises(TypeError) as e:
        assert KBaseAuth()
        assert str(e) == "missing required named argument 'url'"

    with pytest.raises(TypeError) as e:
        assert KBaseAuth(url="foo")
        assert str(e) == "missing required named argument 'cache_max_size'"

    with pytest.raises(TypeError) as e:
        assert KBaseAuth(url="foo", cache_max_size=1)
        assert str(e) == "missing required named argument 'cache_lifetime'"


def test_KBaseAuth_get_token_info(fake_fs):
    with mock_services() as url:
        client = KBaseAuth(url=url, cache_max_size=3, cache_lifetime=3)
        assert client is not None
        client.cache.clear()

        # First fetch of token from service
        token_info = client.get_token_info("foo")
        assert isinstance(token_info, TokenInfo)
        assert token_info.user == "foo"

        # Second should come from the cache. Let's test this by
        # killing the service!
        # TODO: service can have something measurable, like a call count.
        token_info = client.get_token_info("foo")
        assert isinstance(token_info, TokenInfo)
        assert token_info.user == "foo"


def test_KBaseAuth_get_token_info_other_error(fake_fs):
    with mock_services() as url:
        client = KBaseAuth(url=url, cache_max_size=3, cache_lifetime=3)
        assert client is not None
        client.cache.clear()

        # First fetch of token from service
        with pytest.raises(KBaseAuthError):
            client.get_token_info("exception")


def test_KBaseAuth_get_token_info_internal_error(fake_fs):
    with mock_services() as url:
        client = KBaseAuth(url=url, cache_max_size=3, cache_lifetime=3)
        assert client is not None
        client.cache.clear()

        # The call should trigger a JSON decode error, since this mimics
        # an actual, unexpected, unhandled error response with a text
        # body.
        with pytest.raises(ServiceError):
            client.get_token_info("internal_server_error")


def test_KBaseAuth_get_token_info_param_errors(fake_fs):
    client = KBaseAuth(
        url="http://foo/services/auth/api/V2/token",
        cache_max_size=1,
        cache_lifetime=1,
    )
    assert client is not None
    with pytest.raises(TypeError) as e:
        client.get_token_info("")


def test_KBaseAuth_get_username(fake_fs):
    with mock_services() as url:
        client = KBaseAuth(url=url, cache_max_size=3, cache_lifetime=3)
        assert client is not None
        client.cache.clear()

        username = client.get_username("foo")
        assert username == "foo"
