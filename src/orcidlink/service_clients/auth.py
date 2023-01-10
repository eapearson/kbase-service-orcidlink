from orcidlink.lib.config import get_config
from orcidlink.service_clients import authclient2


def get_username(kbase_auth_token: str) -> str:
    auth = authclient2.KBaseAuth(
        auth_url=get_config(["kbase", "services", "Auth2", "url"]),
        cache_lifetime=get_config(["kbase", "services", "Auth2", "tokenCacheLifetime"]) / 1000,
        cache_max_size=get_config(["kbase", "services", "Auth2", "tokenCacheMaxSize"])
    )

    return auth.get_username(kbase_auth_token)
