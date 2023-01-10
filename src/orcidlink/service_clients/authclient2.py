"""
A basic KBase auth client for the Python server.
The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json

import httpx
from cache3 import SafeCache
from pydantic import BaseModel, Field

global_cache = None


class TokenInfo(BaseModel):
    type: str = Field(...)
    id: str = Field(...)
    expires: int = Field(...)
    created: int = Field(...)
    name: str | None = Field(...)
    user: str = Field(...)
    custom: dict = Field(...)
    cachefor: int = Field(...)


class KBaseAuth(object):
    """
    A very basic KBase auth client for the Python server.
    """

    def __init__(self,
                 auth_url: str = None,
                 cache_max_size: int = None,
                 cache_lifetime: int = None):
        """
        Constructor
        """
        if auth_url is None:
            raise TypeError("missing required named argument 'auth_url'")

        if cache_max_size is None:
            raise TypeError("missing required named argument 'cache_max_size'")

        if cache_lifetime is None:
            raise TypeError("missing required named argument 'cache_lifetime'")

        self.auth_url = auth_url

        global global_cache

        if global_cache is None:
            global_cache = SafeCache(max_size=cache_max_size, timeout=cache_lifetime)

        self.cache = global_cache

    def get_token_info(self, token: str) -> TokenInfo:
        token_info = self.cache.get(token)
        if token_info is not None:
            return token_info

        # TODO: timeout needs to be configurable
        try:
            response = httpx.get(self.auth_url, headers={"authorization": token}, timeout=10000)
            # except httpx.HTTPStatusError:
            #     # Note that here we are raising the default exception for the
            #     # httpx library in the case that a deep internal server error
            #     # is thrown without an actual json response. In other words, the
            #     # error is not a JSON-RPC error thrown by the auth2 service itself,
            #     # but some truly internal server error.
            #     # Note that ALL errors returned by stock KBase JSON-RPC 1.1 servers
            #     # are 500.
            #     response.raise_for_status()
            #
            # try:
            json_response = response.json()
        except json.JSONDecodeError as ex:
            # Note that here we are raising the default exception for the
            # httpx library in the case that a deep internal server error
            # is thrown without an actual json response. In other words, the
            # error is not a JSON-RPC error thrown by the auth2 service itself,
            # but some truly internal server error.
            # Note that ALL errors returned by stock KBase JSON-RPC 1.1 servers
            # are 500.
            raise KBaseAuthException(f"Error decoding JSON response: {str(ex)}")

        if not response.is_success:
            # The auth service should return a 500 for all errors
            # Make an attempt to handle a specific auth error
            appcode = json_response['error']['appcode']
            if appcode == 10020:
                raise KBaseAuthInvalidToken('Invalid token')
            else:
                raise KBaseAuthException(json_response['error']['message'])

        token_info = TokenInfo.parse_obj(json_response)
        self.cache.set(token, token_info)
        return token_info

    def get_username(self, token: str) -> str:
        return self.get_token_info(token).user


class KBaseAuthException(Exception):
    pass


class KBaseAuthMissingToken(KBaseAuthException):
    pass


class KBaseAuthInvalidToken(KBaseAuthException):
    pass

# class KBaseAuthException(Exception):
#     def __init__(self, code: int, message: str, long_message: str):
#         super().__init__(message)
#         self.code = code
#         self.message = message
#         self.long_message = long_message
#
#     def to_dict(self):
#         return {
#             'code': self.code,
#             'message': self.message,
#             'long_message': self.long_message
#         }
