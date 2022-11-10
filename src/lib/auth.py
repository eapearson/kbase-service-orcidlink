from lib.config import get_config
from lib.exceptions import KBaseAuthException

from lib import authclient


def get_username(kbase_auth_token):
    auth = authclient.KBaseAuth(
        auth_url=get_config(["kbase", "services", "Auth2", "url"])
    )

    try:
        return auth.get_user(kbase_auth_token)
    except Exception as ex:
        raise KBaseAuthException(
            message="Authentication error",
            upstream_error="Upstream Error",
            exception_string=str(ex)
        )
        # raise error_response("auth", "Authentication error using the token", {
        #     "upstream": {
        #         "error": str(ex)
        #     }
        # })
