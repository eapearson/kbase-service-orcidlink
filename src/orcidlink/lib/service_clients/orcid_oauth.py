from json import JSONDecodeError
from typing import Any, Dict, Optional

import aiohttp
from multidict import CIMultiDict
from pydantic import Field

from orcidlink import model
from orcidlink.lib import exceptions
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.runtime import config


class ORCIDOAuthError(ServiceBaseModel):
    error: str = Field(...)
    error_description: str = Field(...)


class ORCIDOAuthClient:
    """
    An OAuth client supporting various operations.
    """

    url: str

    def __init__(self, url: Optional[str] = None):
        if url is None:
            raise TypeError('the "url" named parameter is required')
        self.base_url: str = url

    def url_path(self, path: str) -> str:
        return f"{self.base_url}/{path}"

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
        content_type_raw = response.headers.get("Content-Type")
        if content_type_raw is None:
            raise exceptions.UpstreamError("No content-type in response")

        content_type, _, _ = content_type_raw.partition(";")
        if content_type != "application/json":
            raise exceptions.UpstreamError(
                f"Expected JSON response, got {content_type}"
            )

        try:
            json_response = await response.json()
        except JSONDecodeError as jde:
            raise exceptions.JSONDecodeError(
                "Error decoding JSON response",
                exceptions.JSONDecodeErrorData(message=str(jde)),
            )

        if response.status == 200:
            return json_response
        else:
            if "error" in json_response:
                return ORCIDOAuthError.model_validate(json_response)
            else:
                raise exceptions.UpstreamError("Unexpected Error Response from ORCID")

    #
    # Revoke ORCID side of link.
    #
    async def revoke_access_token(self, access_token: str) -> None:
        """
        Revokes, or removes, the provided access token, and the associated refresh
        token.

        The ORCID Link record should also be removed. The existing refresh token may not
        be used to create a new token as it will be invalidated as well. The only

        For access token revocation whilst retaining the ability to generate new access
        tokens via refreshing, see the refresh endpoint below.

        See:
        https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/revoke.md
        """
        header = self.header()
        data = self.constrained_data()
        data["token"] = access_token

        # TODO: determine all possible ORCID errors here, or the
        # pattern with which we can return useful info
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url_path("revoke"), headers=header, data=data
            ) as response:
                if response.status != 200:
                    raise exceptions.make_upstream_error(
                        response.status, None, source="revoke_link"
                    )

    #
    # Obtain a new set of tokens for a given refresh token
    #
    async def refresh_token(self, refresh_token: str) -> model.ORCIDAuth:
        """
        Obtain a new set of tokens for a given refresh token

        The ORCID Link record should also be removed. The existing refresh token may not
        be used to create a new token as it will be invalidated as well. The only
        solution is to create a new link.

        See:
        https://github.com/ORCID/ORCID-Source/blob/main/orcid-api-web/tutorial/refresh_tokens.md
        """
        header = self.header()
        data = self.constrained_data()
        data["refresh_token"] = refresh_token
        data["grant_type"] = "refresh_token"
        data["revoke_old"] = "true"

        # TODO: determine all possible ORCID errors here, or the
        # pattern with which we can return useful info
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url_path("token"), headers=header, data=data
            ) as response:
                json_response = await self.handle_json_response(response)

                if isinstance(json_response, ORCIDOAuthError):
                    # This is returned when the main token set (access token, etc.) is
                    # no longer valid,
                    if json_response.error == "unauthorized_client":
                        raise exceptions.AuthorizationRequiredError(
                            json_response.error_description
                        )
                    else:
                        raise exceptions.UpstreamError(json_response.error_description)
                else:
                    return model.ORCIDAuth.model_validate(json_response)

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
                    raise exceptions.UpstreamError(json_response.error_description)
                else:
                    return model.ORCIDAuth.model_validate(json_response)


def orcid_oauth() -> ORCIDOAuthClient:
    """
    Creates an instance of ORCIDOAuthClient for support of the ORCID OAuth API.

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthClient(url=config().orcid_oauth_base_url)
