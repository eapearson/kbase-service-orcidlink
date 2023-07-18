from typing import Any, Coroutine, Tuple

from orcidlink.lib.config import config
from orcidlink.lib.errors import ServiceError
from orcidlink.lib.responses import ErrorResponse
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.service_clients.KBaseAuth import KBaseAuth, TokenInfo


async def get_username(kbase_auth_token: str) -> str:
    auth = KBaseAuth(
        url=config().services.Auth2.url,
        cache_lifetime=int(config().services.Auth2.tokenCacheLifetime / 1000),
        cache_max_size=config().services.Auth2.tokenCacheMaxSize,
    )

    return await auth.get_username(kbase_auth_token)


async def ensure_authorization(
    authorization: str | None,
) -> Tuple[str, TokenInfo]:
    """
    Ensures that the "authorization" value, the KBase auth token, is
    not none. This is a convenience function for endpoints, whose sole
    purpose is to ensure that the provided token is good and valid.
    """
    if authorization is None:
        raise ServiceError(
            error=ErrorResponse[ServiceBaseModel](
                code="missingToken",
                title="Missing Token",
                message="API call requires a KBase auth token",
            ),
            status_code=401,
        )
    auth = KBaseAuth(
        url=config().services.Auth2.url,
        cache_lifetime=int(config().services.Auth2.tokenCacheLifetime / 1000),
        cache_max_size=config().services.Auth2.tokenCacheMaxSize,
    )
    token_info = await auth.get_token_info(authorization)
    return authorization, token_info
