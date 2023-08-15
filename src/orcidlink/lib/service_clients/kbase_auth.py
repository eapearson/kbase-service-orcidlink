"""
A basic KBase auth client for the Python server.
The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json
from typing import Dict

import aiohttp
from cachetools import TTLCache
from pydantic import Field

from orcidlink.lib import errors, exceptions
from orcidlink.lib.type import ServiceBaseModel


class TokenInfo(ServiceBaseModel):
    type: str = Field(...)
    id: str = Field(...)
    expires: int = Field(...)
    created: int = Field(...)
    name: str | None = Field(...)
    user: str = Field(...)
    custom: Dict[str, str] = Field(...)
    cachefor: int = Field(...)


class KBaseAuth(object):
    """
    A very basic KBase auth client for the Python server.
    """

    cache: TTLCache[str, TokenInfo]

    def __init__(
        self,
        url: str,
        timeout: int,
        cache_max_items: int,
        cache_lifetime: int,
    ):
        """
        Constructor
        """
        self.url = url
        self.timeout = timeout
        self.cache_max_items = cache_max_items
        self.cache_lifetime = cache_lifetime

        self.cache: TTLCache[str, TokenInfo] = TTLCache(
            maxsize=self.cache_max_items, ttl=self.cache_lifetime
        )

        # global global_cache
        #
        # if global_cache is None:
        #     global_cache = SafeCache(
        #         max_size=self.cache_max_size, timeout=self.cache_lifetime
        #     )
        #
        # self.cache = global_cache

    # @cachedmethod(lambda self: self.cache, key=partial(hashkey, 'token_info'))
    async def get_token_info(self, token: str) -> TokenInfo:
        if token == "":
            # raise TypeError("Token may not be empty")
            raise exceptions.AuthorizationRequiredError("Token may not be empty")

        cache_value = self.cache.get(token)
        if cache_value is not None:
            return cache_value

        # TODO: timeout needs to be configurable
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.url}/api/V2/token"
                async with session.get(
                    url, headers={"authorization": token}, timeout=10000
                ) as response:
                    json_response = await response.json()
        except aiohttp.ContentTypeError as cte:
            # Raised if it is not application/json
            raise exceptions.ContentTypeError("Wrong content type", cte)
        except json.JSONDecodeError as jde:
            raise exceptions.JSONDecodeError("Error decoding JSON", jde)
        except Exception:
            raise exceptions.InternalServerError("Unexpected error")
        # TODO: convert the below to ServerErrorXX
        if not response.ok:
            # The auth service should return a 500 for all errors
            # Make an attempt to handle a specific auth error
            appcode = json_response["error"]["appcode"]
            json_response["error"]["message"]
            if appcode == 10020:
                raise exceptions.ServiceErrorY(
                    errors.ERRORS.authorization_required,
                    "Invalid token, authorization required",
                )
            elif appcode == 10010:
                raise exceptions.ServiceErrorY(
                    errors.ERRORS.authorization_required,
                    "Token missing, authorization required",
                )
            else:
                raise exceptions.UpstreamError("Error authenticating with auth service")

        token_info: TokenInfo = TokenInfo.model_validate(json_response)
        self.cache[token] = token_info
        return token_info

    async def get_username(self, token: str) -> str:
        token_info = await self.get_token_info(token)
        return token_info.user


# class InvalidResponse(ServiceError):
#     """
#     Raised when a remote service returns an invalid response. E.g. a 500 error with a text response, when the
#     service is only defined to return JSON.
#     """
#
#     pass


# class KBaseAuthErrorInfo(ServiceBaseModel):
#     code: int = Field(...)
#     message: str = Field(...)
#     original_message: str = Field(
#         validation_alias="original-message", serialization_alias="original-message"
#     )


# class KBaseAuthError(Exception):
#     message: str
#     code: int
#     original_message: str

#     def __init__(self, message: str, code: int, original_message: str):
#         super().__init__(message)
#         self.code = code
#         self.message = message
#         self.original_message = original_message

#     def to_obj(self) -> KBaseAuthErrorInfo:
#         return KBaseAuthErrorInfo(
#             code=self.code, message=self.message, original_message=self.original_message
#         )


# class KBaseAuthInvalidToken(KBaseAuthError):
#     def __init__(self, original_message: str):
#         super().__init__("Invalid token", 1020, original_message)
