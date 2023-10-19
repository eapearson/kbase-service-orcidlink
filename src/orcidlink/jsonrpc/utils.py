from typing import Tuple

from orcidlink.jsonrpc.errors import AuthorizationRequiredError
from orcidlink.lib.service_clients.kbase_auth import (
    AccountInfo,
    AuthError,
    KBaseAuth,
    TokenInfo,
    auth_error_to_jsonrpc_error,
)
from orcidlink.runtime import config


async def ensure_authorization2(
    authorization: str | None,
) -> Tuple[str, TokenInfo]:
    """
    Ensures that the "authorization" value, the KBase auth token, is
    not none, otherwise just passes it to the `get_token_info` method
    of the auth client to get the token info.

    This is a convenience function for endpoints, and provides consistent
    error handling. Its sole purpose is to ensure that the provided token is good and
    valid.
    """
    if authorization is None:
        raise AuthorizationRequiredError("Authorization required but missing")

    auth = KBaseAuth(
        url=config().auth_url,
        timeout=config().request_timeout,
    )

    # TODO: rectify with JSON-RPC errors. Ultimately, all API calls will be JSON-RPC,
    # with just some OAuth stuff remaining as "REST-ish"

    try:
        token_info = await auth.get_token_info(authorization)
    except AuthError as ae:
        raise auth_error_to_jsonrpc_error(ae)

    return authorization, token_info


async def ensure_account2(
    authorization: str | None,
) -> Tuple[str, AccountInfo]:
    """ """
    if authorization is None:
        raise AuthorizationRequiredError("Authorization required but missing")

    auth = KBaseAuth(
        url=config().auth_url,
        timeout=config().request_timeout,
    )

    # TODO: rectify with JSON-RPC errors. Ultimately, all API calls will be JSON-RPC,
    # with just some OAuth stuff remaining as "REST-ish"

    try:
        account_info = await auth.get_me(authorization)
    except AuthError as ae:
        raise auth_error_to_jsonrpc_error(ae)

    return authorization, account_info
