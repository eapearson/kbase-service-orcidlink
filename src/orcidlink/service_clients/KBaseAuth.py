"""
A basic KBase auth client for the Python server.
The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json
from typing import Dict, Optional

# import httpx
import aiohttp

# from cache3 import SafeCache  # type: ignore
from cachetools import TTLCache
from pydantic import Field

from orcidlink import model
from orcidlink.lib.errors import ServiceError
from orcidlink.lib.responses import ErrorResponse
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

        self.cache: TTLCache[str, TokenInfo] = TTLCache(
            maxsize=self.cache_max_size, ttl=self.cache_lifetime
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
            raise TypeError("Token may not be empty")

        cache_value = self.cache.get(token)
        if cache_value is not None:
            return cache_value

        # TODO: timeout needs to be configurable
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url, headers={"authorization": token}, timeout=10000
                ) as response:
                    json_response = await response.json()
        except aiohttp.client_exceptions.ContentTypeError as cte:
            # Note that here we are raising the default exception for the
            # httpx library in the case that a deep internal server error
            # is thrown without an actual json response. In other words, the
            # error is not a JSON-RPC error thrown by the auth2 service itself,
            # but some truly internal server error.
            # Note that ALL errors returned by stock KBase JSON-RPC 1.1 servers
            # are 500.
            raise ServiceError(
                error=ErrorResponse[ServiceBaseModel](
                    code="badContentType",
                    title="Received Incorrect Content Type",
                    message="The auth service responded with wrong content type; expected application/json",
                    data=model.JSONDecodeErrorData(
                        status_code=response.status, error=str(cte)
                    ),
                ),
                status_code=502,
            ) from cte
        except json.JSONDecodeError as ex:
            # Note that here we are raising the default exception for the
            # httpx library in the case that a deep internal server error
            # is thrown without an actual json response. In other words, the
            # error is not a JSON-RPC error thrown by the auth2 service itself,
            # but some truly internal server error.
            # Note that ALL errors returned by stock KBase JSON-RPC 1.1 servers
            # are 500.
            raise ServiceError(
                error=ErrorResponse[ServiceBaseModel](
                    code="jsonDecodeError",
                    title="Error Decoding Response",
                    message="The auth service responded with non-JSON content",
                    data=model.JSONDecodeErrorData(
                        status_code=response.status, error=str(ex)
                    ),
                ),
                status_code=502,
            ) from ex
        except Exception as ex:
            print("EXCEPTION!!!!", str(ex), ex.__class__)
            raise ex

        if not response.ok:
            # The auth service should return a 500 for all errors
            # Make an attempt to handle a specific auth error
            appcode = json_response["error"]["appcode"]
            message = json_response["error"]["message"]
            if appcode == 10020:
                raise KBaseAuthInvalidToken("Invalid token")
            else:
                raise KBaseAuthError("Auth Service Error", appcode, message)

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


class KBaseAuthErrorInfo(ServiceBaseModel):
    code: int = Field(...)
    message: str = Field(...)
    original_message: str = Field(alias="original-message")


class KBaseAuthError(Exception):
    message: str
    code: int
    original_message: str

    def __init__(self, message: str, code: int, original_message: str):
        super().__init__(message)
        self.code = code
        self.message = message
        self.original_message = original_message

    def to_obj(self) -> KBaseAuthErrorInfo:
        return KBaseAuthErrorInfo(
            code=self.code, message=self.message, original_message=self.original_message
        )


class KBaseAuthInvalidToken(KBaseAuthError):
    def __init__(self, original_message: str):
        super().__init__("Invalid token", 1020, original_message)
