"""
A basic KBase auth client for the Python server.
The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json
from typing import Optional

import httpx
from cache3 import SafeCache  # type: ignore
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

    def __init__(
        self,
        url: Optional[str] = None,
        cache_max_size: Optional[int] = None,
        cache_lifetime: Optional[int] = None,
    ):
        """
        Constructor
        """
        if url is None:
            raise TypeError("missing required named argument 'url'")
        self.url: str = url

        if cache_max_size is None:
            raise TypeError("missing required named argument 'cache_max_size'")
        self.cache_max_size: int = cache_max_size

        if cache_lifetime is None:
            raise TypeError("missing required named argument 'cache_lifetime'")
        self.cache_lifetime: int = cache_lifetime

        global global_cache

        if global_cache is None:
            global_cache = SafeCache(
                max_size=self.cache_max_size, timeout=self.cache_lifetime
            )

        self.cache = global_cache

    def get_token_info(self, token: str) -> TokenInfo:
        if token is None or token == "":
            raise KBaseAuthMissingToken("Token may not be empty")

        cache_value = self.cache.get(token)
        if cache_value is not None:
            return TokenInfo.parse_obj(cache_value)

        # TODO: timeout needs to be configurable
        try:
            response = httpx.get(
                self.url, headers={"authorization": token}, timeout=10000
            )

            # if response.status_code != 200:

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
            print("ERROR", self.url, response.text)
            raise KBaseAuthException(f"Error decoding JSON response: {str(ex)}")

        if not response.is_success:
            # The auth service should return a 500 for all errors
            # Make an attempt to handle a specific auth error
            appcode = json_response["error"]["appcode"]
            if appcode == 10020:
                raise KBaseAuthInvalidToken("Invalid token")
            else:
                raise KBaseAuthException(json_response["error"]["message"])

        token_info: TokenInfo = TokenInfo.parse_obj(json_response)
        self.cache.set(token, token_info.dict(), timeout=token_info.cachefor)
        return token_info

    def get_username(self, token: str) -> str:
        return self.get_token_info(token).user


class KBaseAuthException(Exception):
    pass


class KBaseAuthMissingToken(KBaseAuthException):
    pass


class KBaseAuthInvalidToken(KBaseAuthException):
    pass
