from orcidlink.lib.config import config
from orcidlink.service_clients import authclient2


##
#

def get_username(kbase_auth_token: str) -> str:
    auth = authclient2.KBaseAuth(
        auth_url=config().kbase.services.Auth2.url,
        cache_lifetime=config().kbase.services.Auth2.tokenCacheLifetime / 1000,
        cache_max_size=config().kbase.services.Auth2.tokenCacheMaxSize
    )

    return auth.get_username(kbase_auth_token)
