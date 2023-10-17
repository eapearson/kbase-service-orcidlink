import json
from typing import Any, Dict

import aiohttp
from multidict import CIMultiDict

from orcidlink import model
from orcidlink.jsonrpc.errors import ContentTypeError, JSONDecodeError, UpstreamError
from orcidlink.lib.service_clients.orcid_oauth_api_errors import (
    OAuthAPIError,
    orcid_oauth_api_to_json_rpc_error,
)
from orcidlink.runtime import config


class ORCIDOAuthAPIClient:
    """
    An OAuth client supporting API operations.

    For interactive endpoints which support 3-legged OAuth flow, see "orcid_oauth_interactive.py"
    """

    url: str

    def __init__(self, url: str):
        self.base_url: str = url

    def url_path(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def header(self) -> CIMultiDict[str]:
        """
        Form the common header for OAuth API calls.

        Note that the API returns JSON (as "application/json"), but accepts data as html
        form encoding ("application/x-www-form-urlencoded"). This is a requirement of
        the OAUth 2.0 3-legged flow.
        """
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
            raise ContentTypeError("No content-type in response")

        content_type, _, _ = content_type_raw.partition(";")
        if content_type != "application/json":
            raise ContentTypeError(f"Expected JSON response, got {content_type}")
        try:
            text_response = await response.text()
            json_response = json.loads(text_response)
        except json.JSONDecodeError as jde:
            raise JSONDecodeError(
                "Error decoding JSON response",
            ) from jde

        if response.status == 200:
            return json_response
        else:
            if "error" in json_response:
                return OAuthAPIError.model_validate(json_response)
            else:
                raise UpstreamError(data={"upstream_error": json_response})

    async def handle_empty_response(
        self, response: aiohttp.ClientResponse
    ) -> None | OAuthAPIError:
        """
        Given a response from the ORCID OAuth service, as an aiohttp
        response object, extract and return JSON from the body, handling
        any erroneous conditions.
        """
        text_response = await response.text()

        #
        # The "normal" response
        #
        if len(text_response) == 0:
            return None

        if response.status == 200:
            raise UpstreamError("Expected empty response")

        try:
            json_response = json.loads(text_response)
        except json.JSONDecodeError as jde:
            raise JSONDecodeError(
                "Error decoding JSON response",
            ) from jde

        if "error" in json_response:
            return OAuthAPIError.model_validate(json_response)
        else:
            raise UpstreamError(data={"upstream_error": json_response})

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
                empty_response = await self.handle_empty_response(response)
                if empty_response is None:
                    return

                if isinstance(empty_response, OAuthAPIError):
                    raise orcid_oauth_api_to_json_rpc_error(empty_response)

                # This is returned when the main token set (access token, etc.) is
                # no longer valid,
                # if empty_response.error == "unauthorized_client":
                #     raise NotAuthorizedError(empty_response.error_description)
                # else:
                #     raise UpstreamError(empty_response.error_description)

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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url_path("token"), headers=header, data=data
            ) as response:
                json_response = await self.handle_json_response(response)

                if isinstance(json_response, OAuthAPIError):
                    raise orcid_oauth_api_to_json_rpc_error(json_response)
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
                if isinstance(json_response, OAuthAPIError):
                    raise orcid_oauth_api_to_json_rpc_error(json_response)
                else:
                    return model.ORCIDAuth.model_validate(json_response)


def orcid_oauth_api() -> ORCIDOAuthAPIClient:
    """
    Creates an instance of ORCIDOAuthClient for support of the ORCID OAuth API.

    Note that this is

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthAPIClient(url=config().orcid_oauth_base_url)
