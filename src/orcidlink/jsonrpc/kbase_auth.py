"""
A basic KBase auth client for the Python server.

The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json
from typing import Any, Dict, List

import aiohttp
from pydantic import Field

from orcidlink.jsonrpc.errors import (
    AuthorizationRequiredError,
    ContentTypeError,
    JSONDecodeError,
    UpstreamError,
)

# from orcidlink.lib import error
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


class Identity(ServiceBaseModel):
    id: str = Field(...)
    provider: str = Field(...)
    provusername: str = Field(...)


class Role(ServiceBaseModel):
    id: str = Field(...)
    desc: str = Field(...)


class PolicyAgreement(ServiceBaseModel):
    id: str = Field(...)
    agreedon: int = Field(...)


class AccountInfo(ServiceBaseModel):
    user: str = Field(...)
    display: str = Field(...)
    email: str = Field(...)
    created: int = Field(...)
    lastlogin: int = Field(...)
    local: bool = Field(...)
    roles: List[Role] = Field(...)
    customroles: List[str] = Field(...)
    idents: List[Identity] = Field(...)
    policyids: List[PolicyAgreement]


class KBaseAuth(object):
    """
    A very basic KBase auth client for the Python server.
    """

    def __init__(
        self,
        url: str,
        timeout: int,
    ):
        """
        Constructor
        """
        self.url = url
        self.timeout = timeout

    async def _get(self, path: str, authorization: str) -> Any:
        """
        General purpose "GET request" request and response implementation for the auth
        service V2 api.

        It can handle any endpoint which uses the GET request method, as it is
        agnostic about the structure of the response.

        It raises several errors, under the following conditions:
        exceptions.ContentTypeError - if the wrong content type (not application/json)
          is returned (raised by aiohttp)
        exceptions.JSONDecodeError - if the response does not parse correctly as
          JSON (raised by aiohttp)
        exceptions.ServiceErrorY (401 - auth required) - if the error returned by the
          auth service is 10020 (invalid token
        exceptions.UpstreamError - for any other error reported by the auth service
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.url}/api/V2/{path}"
                async with session.get(
                    url, headers={"authorization": authorization}, timeout=self.timeout
                ) as response:
                    json_result = await response.json()

        except aiohttp.ContentTypeError as cte:
            # Raised if it is not application/json
            # data = exceptions.ContentTypeErrorData()
            # if cte.headers is not None:
            #     data.originalContentType = cte.headers["content-type"]
            raise ContentTypeError("Wrong content type") from cte  # , data=data)

        except json.JSONDecodeError as jde:
            raise JSONDecodeError(
                "Error decoding JSON response",
                # JSONDecodeErrorData(message=str(jde)),
            ) from jde

        except aiohttp.ClientConnectionError:
            # TODO: should be own bespoke error?
            raise UpstreamError("Error connecting to auth service")

        if not response.ok:
            # We don't care about the HTTP response code, just the appcode in the
            # response data.
            appcode = json_result["error"]["appcode"]
            json_result["error"]["message"]
            if appcode == 10020:
                raise AuthorizationRequiredError()
            else:
                raise UpstreamError("Error authenticating with auth service")

        return json_result

    async def get_token_info(self, token: str) -> TokenInfo:
        """
        Fetches token information from the auth service and returns it in a
        Pydantic class matching the original structure.
        """
        json_result = await self._get("token", token)

        return TokenInfo.model_validate(json_result)

    async def get_me(self, token: str) -> AccountInfo:
        """
        Fetches user account information from the auth service and returns it in a
        Pydantic class matching the original structure.
        """
        if token == "":
            raise AuthorizationRequiredError("Token may not be empty")

        json_result = await self._get("me", token)

        return AccountInfo.model_validate(json_result)
