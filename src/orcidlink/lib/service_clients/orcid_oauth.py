import json
from typing import Any, Dict

import aiohttp
from multidict import CIMultiDict

from orcidlink import model
from orcidlink.jsonrpc.errors import (
    ContentTypeError,
    JSONDecodeError,
    NotAuthorizedError,
    ORCIDUnauthorizedClient,
    UpstreamError,
)
from orcidlink.lib.service_clients.orcid_api_errors import OAuthError
from orcidlink.runtime import config


class ORCIDOAuthClient:
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
        content_length_raw = response.headers.get("Content-Length")
        if content_length_raw is None:
            raise UpstreamError("No content length in response")
        content_length = int(content_length_raw)
        if content_length == 0:
            # We don't have any cases of an empty response, so consider
            # this an error. We need to cover this case, even though we
            # don't expect it in reality.
            raise UpstreamError("Unexpected empty body")

        content_type_raw = response.headers.get("Content-Type")

        if content_type_raw is None:
            raise ContentTypeError("No content-type in response")

        content_type, _, _ = content_type_raw.partition(";")
        if content_type != "application/json":
            raise ContentTypeError(f"Expected JSON response, got {content_type}")
        try:
            json_response = await response.json()
        except json.JSONDecodeError as jde:
            raise JSONDecodeError(
                "Error decoding JSON response",
            ) from jde

        if response.status == 200:
            return json_response
        else:
            if "error" in json_response:
                return OAuthError.model_validate(json_response)
            else:
                raise UpstreamError("Unexpected Error Response from ORCID")

    async def handle_empty_response(
        self, response: aiohttp.ClientResponse
    ) -> None | OAuthError:
        """
        Given a response from the ORCID OAuth service, as an aiohttp
        response object, extract and return JSON from the body, handling
        any erroneous conditions.
        """
        content_length_raw = response.headers.get("Content-Length")
        if content_length_raw is None:
            # raise some error?
            raise UpstreamError("No content length in response")

        # We don't bother handling a malformed content length header; that will
        # just throw a ValueError which will percolate up through FastAPI/Starlette
        # and become an internal server error, which is good enough.
        content_length = int(content_length_raw)
        if content_length == 0:
            # This is our normal condition; we exit early.
            return None

        if response.status == 200:
            raise UpstreamError("Expected empty response")

        content_type_raw = response.headers.get("Content-Type")
        if content_type_raw is None:
            raise ContentTypeError("No content-type in response")

        content_type, _, _ = content_type_raw.partition(";")
        if content_type != "application/json":
            raise ContentTypeError(f"Expected JSON response, got {content_type}")

        try:
            json_response = await response.json()
        except json.JSONDecodeError as jde:
            raise JSONDecodeError(
                "Error decoding JSON response",
                # exceptions.JSONDecodeErrorData(message=str(jde)),
            ) from jde

        if "error" in json_response:
            return OAuthError.model_validate(json_response)
        else:
            raise UpstreamError("Unexpected Error Response from ORCID")

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
                # if response.status != 200:
                #     raise exceptions.make_upstream_error(
                #         response.status, None, source="revoke_link"
                #     )

                # This is returned when the main token set (access token, etc.) is
                # no longer valid,
                if empty_response.error == "unauthorized_client":
                    raise NotAuthorizedError(empty_response.error_description)
                else:
                    raise UpstreamError(empty_response.error_description)

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

                if isinstance(json_response, OAuthError):
                    # This is returned when the main token set (access token, etc.) is
                    # no longer valid,
                    if json_response.error == "unauthorized_client":
                        raise ORCIDUnauthorizedClient(json_response.error_description)
                    else:
                        raise UpstreamError(json_response.error_description)
                else:
                    return model.ORCIDAuth.model_validate(json_response)


def orcid_oauth() -> ORCIDOAuthClient:
    """
    Creates an instance of ORCIDOAuthClient for support of the ORCID OAuth API.

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthClient(url=config().orcid_oauth_base_url)
