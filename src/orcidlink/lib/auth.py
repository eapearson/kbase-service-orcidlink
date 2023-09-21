from typing import Tuple

from orcidlink.lib import exceptions
from orcidlink.lib.service_clients.kbase_auth import AccountInfo, KBaseAuth, TokenInfo
from orcidlink.runtime import config

"""
A set of convenience functions for usage by endpoint handlers to ensure that a 
KBase auth token is valid, and as a side benefit, return information associted
with the token such as the token and account info.
"""


async def ensure_authorization(
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
        raise exceptions.AuthorizationRequiredError(
            "Authorization required but missing"
        )

    auth = KBaseAuth(
        url=config().auth_url,
        timeout=config().request_timeout,
        # cache_lifetime=config().token_cache_lifetime,
        # cache_max_items=config().token_cache_lifetime,
    )
    token_info = await auth.get_token_info(authorization)
    return authorization, token_info


async def ensure_account(
    authorization: str | None,
) -> Tuple[str, AccountInfo]:
    """
    Ensures that the "authorization" value, the KBase auth token, is
    not none. This is a convenience function for endpoints, and provides consistent
    error handling. Its sole purpose is to ensure that the provided token is good and
    valid.
    """
    if authorization is None or authorization == "":
        raise exceptions.AuthorizationRequiredError(
            "Authorization required but missing"
        )

    auth = KBaseAuth(
        url=config().auth_url,
        timeout=config().request_timeout,
        # cache_lifetime=config().token_cache_lifetime,
        # cache_max_items=config().token_cache_lifetime,
    )
    account_info = await auth.get_me(authorization)
    return authorization, account_info
