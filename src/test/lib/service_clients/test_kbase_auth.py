import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from unittest import mock

import pytest

from orcidlink.lib import errors, exceptions
from orcidlink.lib.service_clients.kbase_auth import KBaseAuth, TokenInfo


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT) as [_, _, url, port]:
            yield url


#
# Auth Client


def test_kbase_auth_constructor_minimal():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        client = KBaseAuth(url="foo", timeout=1, cache_max_items=1, cache_lifetime=1)
        assert client is not None


async def test_kbase_auth_get_token_info():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1, cache_max_items=3, cache_lifetime=3)
            assert client is not None
            client.cache.clear()

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
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1, cache_max_items=3, cache_lifetime=3)
            assert client is not None
            client.cache.clear()

            with pytest.raises(exceptions.ServiceErrorY):
                await client.get_token_info("exception")


async def test_kbase_auth_get_token_info_internal_error():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1, cache_max_items=3, cache_lifetime=3)
            assert client is not None
            client.cache.clear()

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(exceptions.ContentTypeError):
                await client.get_token_info("internal_server_error")


async def test_kbase_auth_get_token_info_no_token():
    """
    We can't actually replicate a "no token" error, as we defend around that
    condition, but we can simulate it with the special token "no_token" set up
    in the mock auth service.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services() as url:
            client = KBaseAuth(url=url, timeout=1, cache_max_items=3, cache_lifetime=3)
            assert client is not None
            client.cache.clear()

            # The call should trigger a JSON decode error, since this mimics
            # an actual, unexpected, unhandled error response with a text
            # body.
            with pytest.raises(
                exceptions.ServiceErrorY, match="Token missing, authorization required"
            ) as kae:
                await client.get_token_info("no_token")

            # error = kae.value.to_obj()
            assert kae.value.error.code == errors.ERRORS.authorization_required.code
            assert kae.value.error.title == errors.ERRORS.authorization_required.title
            assert kae.value.message == "Token missing, authorization required"


async def test_kbase_auth_get_token_info_param_errors():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        client = KBaseAuth(
            url="http://foo/services/auth",
            timeout=1,
            cache_max_items=1,
            cache_lifetime=1,
        )
        assert client is not None
        with pytest.raises(exceptions.AuthorizationRequiredError) as e:
            await client.get_token_info("")
