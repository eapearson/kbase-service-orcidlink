import contextlib

import pytest
from orcidlink.service_clients import authclient2
from orcidlink.service_clients.authclient2 import TokenInfo
from test.mocks.mock_contexts import mock_auth_service, no_stderr


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service() as [_, _, url]:
            yield url


#
# Auth Client
#

def test_KBaseAuth_constructor_minimal():
    client = authclient2.KBaseAuth(
        auth_url="foo",
        cache_max_size=1,
        cache_lifetime=1
    )
    assert client is not None


def test_KBaseAuth_constructor_parameter_errors():
    with pytest.raises(TypeError) as e:
        assert authclient2.KBaseAuth()
        assert str(e) == "missing required named argument 'auth_url'"

    with pytest.raises(TypeError) as e:
        assert authclient2.KBaseAuth(auth_url="foo")
        assert str(e) == "missing required named argument 'cache_max_size'"

    with pytest.raises(TypeError) as e:
        assert authclient2.KBaseAuth(
            auth_url="foo",
            cache_max_size=1
        )
        assert str(e) == "missing required named argument 'cache_lifetime'"


def test_KBaseAuth_get_token_info():
    with mock_services() as url:
        client = authclient2.KBaseAuth(
            auth_url=url,
            cache_max_size=3,
            cache_lifetime=3
        )
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


def test_KBaseAuth_get_token_info_missing_token():
    with mock_services() as url:
        client = authclient2.KBaseAuth(
            auth_url=url,
            cache_max_size=3,
            cache_lifetime=3
        )
        assert client is not None
        client.cache.clear()

        # First fetch of token from service
        with pytest.raises(authclient2.KBaseAuthInvalidToken):
            client.get_token_info("x")


def test_KBaseAuth_get_token_info_other_error():
    with mock_services() as url:
        client = authclient2.KBaseAuth(
            auth_url=url,
            cache_max_size=3,
            cache_lifetime=3
        )
        assert client is not None
        client.cache.clear()

        # First fetch of token from service
        with pytest.raises(authclient2.KBaseAuthException):
            client.get_token_info("exception")


def test_KBaseAuth_get_token_info_internal_error():
    with mock_services() as url:
        client = authclient2.KBaseAuth(
            auth_url=url,
            cache_max_size=3,
            cache_lifetime=3
        )
        assert client is not None
        client.cache.clear()

        # The call should trigger a JSON decode error, since this mimics
        # an actual, unexpected, unhandled internal error with a text
        # response.
        with pytest.raises(authclient2.KBaseAuthException):
            client.get_token_info("internal_server_error")


def test_KBaseAuth_get_token_info_param_errors():
    client = authclient2.KBaseAuth(
        auth_url="http://foo/services/auth/api/V2/token",
        cache_max_size=1,
        cache_lifetime=1
    )
    assert client is not None
    with pytest.raises(TypeError) as e:
        client.get_token_info()


def test_KBaseAuth_get_username():
    with mock_services() as url:
        client = authclient2.KBaseAuth(
            auth_url=url,
            cache_max_size=3,
            cache_lifetime=3
        )
        assert client is not None
        client.cache.clear()

        username = client.get_username("foo")
        assert username == "foo"
