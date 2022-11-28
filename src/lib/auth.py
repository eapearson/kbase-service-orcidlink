from lib.config import get_config

from lib import authclient


def get_username(kbase_auth_token):
    auth = authclient.KBaseAuth(
        auth_url=get_config(["kbase", "services", "Auth2", "url"])
    )

    # try:
    return auth.get_user(kbase_auth_token)
