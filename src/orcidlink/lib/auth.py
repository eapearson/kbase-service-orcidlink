from typing import Tuple

from orcidlink.jsonrpc.errors import AlreadyLinkedError
from orcidlink.lib.responses import UIError
from orcidlink.lib.service_clients.kbase_auth import (
    AuthError,
    KBaseAuth,
    TokenInfo,
    auth_error_to_ui_error,
)
from orcidlink.runtime import config

"""
A set of convenience functions for usage by endpoint handlers to ensure that a 
KBase auth token is valid, and as a side benefit, return information associted
with the token such as the token and account info.
"""


async def ensure_authorization_ui(
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
        raise UIError(
            AlreadyLinkedError.CODE,
            "The chosen ORCID account is already linked to another KBase account",
        )

    auth = KBaseAuth(
        url=config().auth_url,
        timeout=config().request_timeout,
    )
    try:
        token_info = await auth.get_token_info(authorization)
    except AuthError as ae:
        raise auth_error_to_ui_error(ae)

    return authorization, token_info


# async def ensure_account(
#     authorization: str | None,
# ) -> Tuple[str, AccountInfo]:
#     """
#     Ensures that the "authorization" value, the KBase auth token, is
#     not none. This is a convenience function for endpoints, and provides consistent
#     error handling. Its sole purpose is to ensure that the provided token is good and
#     valid.
#     """
#     if authorization is None or authorization == "":
#         raise exceptions.AuthorizationRequiredError(
#             "Authorization required but missing"
#         )

#     auth = KBaseAuth(
#         url=config().auth_url,
#         timeout=config().request_timeout,
#         # cache_lifetime=config().token_cache_lifetime,
#         # cache_max_items=config().token_cache_lifetime,
#     )
#     account_info = await auth.get_me(authorization)
#     return authorization, account_info
