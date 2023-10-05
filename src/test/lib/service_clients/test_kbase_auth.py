import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from unittest import mock

import pytest

from orcidlink.jsonrpc.errors import ContentTypeError, JSONDecodeError, UpstreamError
from orcidlink.lib.service_clients.kbase_auth import (
    AccountInfo,
    AuthError,
    AuthorizationRequiredAuthError,
    ContentTypeAuthError,
    JSONDecodeAuthError,
    KBaseAuth,
    OtherAuthError,
    TokenInfo,
    auth_error_to_jsonrpc_error,
)


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT) as [_, _, url, port]:
            yield url


#
# Auth Client
#


def test_kbase_auth_constructor_minimal():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        client = KBaseAuth(url="foo", timeout=1)
        assert client is not None


async def test_kbase_auth_get_token_info():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None
            # client.cache.clear()

            # First fetch of token from service
            token_info = await client.get_token_info("foo")
            assert isinstance(token_info, TokenInfo)
            assert token_info.user == "foo"

            # Second should come from the cache. Let's test this by
            # killing the service!
            # TODO: service can have something measurable, like a call count.
            token_info = await client.get_token_info("foo")
            assert isinstance(token_info, TokenInfo)
            assert token_info.user == "foo"


async def test_kbase_auth_get_token_info_other_error():
    """
    An invalid token should raise an AuthorizationRequiredError.

    An invalid token is some token that the auth service rejects as "invalid" -
    which may be poorly formed (never was a token), an expired token,
    or a revoked token. In such a case, the token is treated as if it
    didn't exist, which is why the error is that authorization is required.
    (Even though provided - so this is a somewhat confusing situation to
    consider, at first.)
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            with pytest.raises(AuthorizationRequiredAuthError):
                await client.get_token_info("invalid_token")


async def test_kbase_auth_get_token_info_internal_error():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None
            # client.cache.clear()

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(ContentTypeAuthError):
                await client.get_token_info("internal_server_error")


async def test_kbase_auth_get_token_info_param_errors():
    """ """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        client = KBaseAuth(
            url="http://foo/services/auth",
            timeout=1,
        )
        assert client is not None
        with pytest.raises(OtherAuthError):
            await client.get_token_info("")


async def test_kbase_auth_get_token_info_other_upstream_error():
    """
    We can't actually replicate a "no token" error, as we defend around that
    condition, but we can simulate it with the special token "no_token" set up
    in the mock auth service.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(
                OtherAuthError, match="Error authenticating with auth service"
            ) as kae:
                await client.get_token_info("other_error")

            json_rpc_error = auth_error_to_jsonrpc_error(kae.value)
            assert isinstance(json_rpc_error, UpstreamError)
            assert json_rpc_error.CODE == UpstreamError.CODE


async def test_kbase_auth_get_token_info_bad_json():
    """
    In rare cases, e.g. a "real" 500, the response is text/plain due to the way web
    app servers work!
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(
                JSONDecodeAuthError, match="Error decoding JSON response"
            ) as kae:
                await client.get_token_info("text_json")

            json_rpc_error = auth_error_to_jsonrpc_error(kae.value)
            assert isinstance(json_rpc_error, JSONDecodeError)
            assert json_rpc_error.CODE == JSONDecodeError.CODE


async def test_kbase_auth_get_token_info_bad_content_type():
    """
    In rare cases, e.g. a "real" 500, the response is text/plain due to the way web
    app servers work!
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(ContentTypeAuthError, match="Wrong content type") as err:
                await client.get_token_info("bad_content_type")

            json_rpc_error = auth_error_to_jsonrpc_error(err.value)
            assert isinstance(json_rpc_error, ContentTypeError)
            assert json_rpc_error.CODE == ContentTypeError.CODE


def test_kbase_auth_auth_error_to_jsonrpc_error():
    """
    Covers one case in the conversion "switch", which does
    actually occur in the wild.
    """
    json_rpc_error = auth_error_to_jsonrpc_error(AuthError("fooey"))
    assert isinstance(json_rpc_error, UpstreamError)


async def test_kbase_auth_get_me():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            account_info = await client.get_me("foo")
            assert isinstance(account_info, AccountInfo)
            assert account_info.user == "foo"


async def test_kbase_auth_get_me_param_errors():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1)
            assert client is not None

            with pytest.raises(AuthorizationRequiredAuthError):
                await client.get_me("")


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_auth_error():
#     auth_error = AuthError(123, "my message")
#     as_rpc_error = auth_error.to_json_rpc_error()
#     assert as_rpc_error.code == 123
#     assert as_rpc_error.message == "my message"
#     assert as_rpc_error.data is None

#     auth_error = AuthError(123, "my message", {"foo": "bar"})
#     as_rpc_error = auth_error.to_json_rpc_error()
#     assert as_rpc_error.code == 123
#     assert as_rpc_error.message == "my message"
#     assert as_rpc_error.data == {"foo": "bar"}
