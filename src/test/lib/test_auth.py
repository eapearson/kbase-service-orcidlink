import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from test.mocks.testing_utils import generate_kbase_token
from unittest import mock

import pytest

from orcidlink.lib.auth import ensure_authorization_ui
from orcidlink.lib.responses import UIError

# from orcidlink.lib.auth import ensure_account, ensure_authorization
from orcidlink.lib.service_clients.kbase_auth import TokenInfo


@contextlib.contextmanager
def mock_services():
    """
    Wraps stderr suppression and the mock auth service for convenient usage by
    tests below.
    """
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


@pytest.fixture(name="fake_fs")
def fake_fs_fixture(fs):
    """
    An in-memory filesystem with a hole cut out to expose the real test data
    directory so that tests can load test data.
    """
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


async def test_ensure_authorization():
    """
    Ensures that the convenience function `ensure_authorization` works under
    the happy path - a valid token results in the associated token information.

    Note that the setup for the auth service ensures that token that begins with
    "foo" matches the auth info in the "get-token-foo.json" test data file.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            foo_token = generate_kbase_token("foo")
            authorization, value = await ensure_authorization_ui(foo_token)
            assert isinstance(authorization, str)
            assert authorization == foo_token
            assert isinstance(value, TokenInfo)
            assert value.name == "Foo User"


async def test_ensure_authorization_error_invalid_authorization():
    """
    Ensures that the convenience function `ensure_authorization` raises the expected
    errors when a token is empty or invalid.

    There are several conditions for this:
    - no authorization (None) - triggered with no Authorization header is present
    - invalid token - when a token has expired, has been revoked at the auth
        service, or is plain incorrect.

    Note that all service endpoints apply a basic requirement for the
    authorization header, so other variants like empty string, etc.
    are not possible.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with pytest.raises(UIError):  # , match="Authorization required"
                await ensure_authorization_ui(None)

            with pytest.raises(
                # exceptions.ServiceErrorY, match="Invalid token, authorization
                # required"
                UIError
            ):
                await ensure_authorization_ui(generate_kbase_token("blarmy"))


# async def test_ensure_account():
#     """
#     Ensures that the convenience function `ensure_authorization` works under
#     the happy path - a valid token results in the associated token information.

#     Note that the setup for the auth service ensures that token that begins with
#     "foo" matches the auth info in the "get-me-foo.json" test data file.
#     """
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         with mock_services():
#             foo_token = generate_kbase_token("foo")
#             authorization, account_info = await ensure_account(foo_token)
#             assert isinstance(authorization, str)
#             assert authorization == foo_token
#             assert isinstance(account_info, AccountInfo)
#             assert account_info.display == "Foo F. Foofer"


# async def test_ensure_account_error_invalid_authorization():
#     """
#     Ensures that the convenience function `ensure_authorization` raises the expected
#     errors when a token is empty or invalid.

#     There are several conditions for this:
#     - no authorization (None) - triggered with no Authorization header is present
#     - invalid token - when a token has expired, has been revoked at the auth
#         service, or is plain incorrect.

#     Note that all service endpoints apply a basic requirement for the
#     authorization header, so other variants like empty string, etc.
#     are not possible.
#     """
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         with mock_services():
#             with pytest.raises(
#                 exceptions.AuthorizationRequiredError,
#                 match="Authorization required but missing",
#             ):
#                 await ensure_account(None)

#             with pytest.raises(
#                 exceptions.ServiceErrorY, match="Invalid token, authorization required"
#             ):
#                 await ensure_authorization(generate_kbase_token("blarmy"))
