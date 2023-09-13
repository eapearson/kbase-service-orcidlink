"""
A basic KBase auth client for the Python server.

The SDK version has been modified to integrate with this codebase, such as
using httpx, pydantic models.
"""
import json
from typing import Any, Dict, List

import aiohttp
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
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.url}/api/V2/{path}"
                async with session.get(
                    url, headers={"authorization": authorization}, timeout=self.timeout
                ) as response:
                    json_result = await response.json()

        except aiohttp.ContentTypeError as cte:
            # Raised if it is not application/json
            data = exceptions.ContentTypeErrorData()
            if cte.headers is not None:
                data.originalContentType = cte.headers["content-type"]
            raise exceptions.ContentTypeError("Wrong content type", data=data)
        except json.JSONDecodeError as jde:
            raise exceptions.JSONDecodeError(
                "Error decoding JSON response",
                exceptions.JSONDecodeErrorData(message=str(jde)),
            )

        if not response.ok:
            # We don't care about the HTTP response code, just the appcode in the
            # response data.
            appcode = json_result["error"]["appcode"]
            json_result["error"]["message"]
            if appcode == 10020:
                raise exceptions.ServiceErrorY(
                    errors.ERRORS.authorization_required,
                    "Invalid token, authorization required",
                )
            else:
                raise exceptions.UpstreamError("Error authenticating with auth service")

        return json_result

    async def get_token_info(self, token: str) -> TokenInfo:
        if token == "":
            raise exceptions.AuthorizationRequiredError("Token may not be empty")

        json_result = await self._get("token", token)

        return TokenInfo.model_validate(json_result)

    async def get_me(self, token: str) -> AccountInfo:
        if token == "":
            raise exceptions.AuthorizationRequiredError("Token may not be empty")

        json_result = await self._get("me", token)

        return AccountInfo.model_validate(json_result)
