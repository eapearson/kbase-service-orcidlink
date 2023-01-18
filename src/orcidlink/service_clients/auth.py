from orcidlink.lib.config import config
from orcidlink.service_clients.KBaseAuth import KBaseAuth


##
#


def get_username(kbase_auth_token: str) -> str:
    auth = KBaseAuth(
        auth_url=config().services.Auth2.url,
        cache_lifetime=int(config().services.Auth2.tokenCacheLifetime / 1000),
        cache_max_size=config().services.Auth2.tokenCacheMaxSize,
    )

    return auth.get_username(kbase_auth_token)
