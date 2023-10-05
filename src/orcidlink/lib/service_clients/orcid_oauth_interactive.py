import json
from typing import Any, Dict

import aiohttp
from multidict import CIMultiDict
from pydantic import Field

from orcidlink import model
from orcidlink.jsonrpc.errors import ContentTypeError, JSONDecodeError, UpstreamError
from orcidlink.lib.responses import UIError
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.runtime import config


class ORCIDOAuthError(ServiceBaseModel):
    error: str = Field(...)
    error_description: str = Field(...)


class ORCIDOAuthInteractiveClient:
    """
    An OAuth client supporting various operations.
    """

    url: str

    def __init__(self, url: str):
        self.base_url: str = url

    def header(self) -> CIMultiDict[str]:
        return CIMultiDict(
            [
                ("Accept", "application/json"),
                ("Content-Type", "application/x-www-form-urlencoded"),
            ]
        )

    def constrained_data(self) -> Dict[str, str]:
        return {
            "client_id": config().orcid_client_id,
            "client_secret": config().orcid_client_secret,
        }

    async def handle_json_response(self, response: aiohttp.ClientResponse) -> Any:
        """
        Given a response from the ORCID OAuth service, as an aiohttp
        response object, extract and return JSON from the body, handling
        any erroneous conditions.
        """
        content_length_raw = response.headers.get("Content-Length")
        if content_length_raw is None:
            raise UIError(UpstreamError.CODE, "No content length in response")
        content_length = int(content_length_raw)
        if content_length == 0:
            # We don't have any cases of an empty response, so consider
            # this an error. We need to cover this case, even though we
            # don't expect it in reality.
            raise UIError(UpstreamError.CODE, "Unexpected empty body")

        content_type_raw = response.headers.get("Content-Type")

        if content_type_raw is None:
            raise UIError(ContentTypeError.CODE, "No content-type in response")

        content_type, _, _ = content_type_raw.partition(";")
        if content_type != "application/json":
            raise UIError(
                ContentTypeError.CODE, f"Expected JSON response, got {content_type}"
            )
        try:
            json_response = await response.json()
        except json.JSONDecodeError as jde:
            raise UIError(JSONDecodeError.CODE, "Error decoding JSON response") from jde

        if response.status == 200:
            return json_response
        else:
            if "error" in json_response:
                return ORCIDOAuthError.model_validate(json_response)
            else:
                raise UIError(
                    UpstreamError.CODE, "Unexpected Error Response from ORCID"
                )

    async def exchange_code_for_token(self, code: str) -> model.ORCIDAuth:
        """
        Exchange the temporary token from ORCID for the authorized token.

        ORCID does not specifically document this, but refers to the OAuth spec:
        https://datatracker.ietf.org/doc/html/rfc8693.

        Error structure defined here:
        https://www.rfc-editor.org/rfc/rfc6749#section-5.2
        """
        header = self.header()
        header["accept"] = "application/json"
        data = self.constrained_data()
        data["grant_type"] = "authorization_code"
        data["code"] = code

        # Note that the redirect uri below is just for the api - it is not actually used
        # for redirection in this case.
        # TODO: investigate and point to the docs, because this is weird.
        # TODO: put in orcid client!
        data[
            "redirect_uri"
        ] = f"{config().orcidlink_url}/linking-sessions/oauth/continue"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config().orcid_oauth_base_url}/token", headers=header, data=data
            ) as response:
                json_response = await self.handle_json_response(response)
                if isinstance(json_response, ORCIDOAuthError):
                    # TODO: also provide the OAUTH error code; in fact, this should be
                    # an OAUTHError type, not Upstream error...
                    raise UIError(UpstreamError.CODE, json_response.error_description)
                else:
                    return model.ORCIDAuth.model_validate(json_response)


def orcid_oauth_interactive() -> ORCIDOAuthInteractiveClient:
    """
    Creates an instance of ORCIDOAuthInteractiveClient for support of the ORCID OAuth API.

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthInteractiveClient(url=config().orcid_oauth_base_url)
