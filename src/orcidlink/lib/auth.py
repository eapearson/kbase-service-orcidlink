from typing import Tuple

from orcidlink.lib import errors, exceptions
from orcidlink.lib.config import Config2
from orcidlink.lib.service_clients.kbase_auth import KBaseAuth, TokenInfo

"""
A 
"""


async def get_username(authorization: str) -> str:
    """
    Given a KBase browser auth token (aka "kbase_session"), return the username associated with the
    user account.

    Note that this relies extensively upon the "config" module, which in turn relies upon a
    configuration file being available in the file sysresponsestem.
    """
    config = Config2()
    auth_client = KBaseAuth(
        url=config.get_auth_url(),
        timeout=config.get_request_timeout(),
        cache_lifetime=config.get_cache_lifetime(),
        cache_max_items=config.get_cache_lifetime(),
    )

    return (await auth_client.get_token_info(authorization)).user


async def ensure_authorization(
    authorization: str | None,
) -> Tuple[str, TokenInfo]:
    """
    Ensures that the "authorization" value, the KBase auth token, is
    not none. This is a convenience function for endpoints, and provides consistent
    error handling. Its sole purpose is to ensure that the provided token is good and valid.
    """
    if authorization is None or authorization == "":
        raise exceptions.AuthorizationRequiredError(
            "Authorization required but missing"
        )

    config = Config2()
    auth = KBaseAuth(
        url=config.get_auth_url(),
        timeout=config.get_request_timeout(),
        cache_lifetime=config.get_cache_lifetime(),
        cache_max_items=config.get_cache_max_items(),
    )
    token_info = await auth.get_token_info(authorization)
    return authorization, token_info


# def ensure_authorization_cookie(
#     kbase_session: str | None, kbase_session_backup: str | None
# ) -> Tuple[str, TokenInfo]:
#     """
#     Ensures that the "authorization" value, the KBase auth token, is
#     not none. This is a convenience function for endpoints, whose sole
#     purpose is to ensure that the provided token is good and valid.
#     """
#     authorization = kbase_session or kbase_session_backup
#     if authorization is None or authorization == "":
#         raise Exception("Authorization required")

#     config = Config2()
#     auth = KBaseAuth(
#         url=config.get_auth_url(),
#         timeout=config.get_request_timeout(),
#         cache_lifetime=config.get_cache_lifetime(),
#         cache_max_items=config.get_cache_max_items(),
#     )
#     token_info = auth.get_token_info(authorization)

#     return authorization, token_info
