import json
from json import JSONDecodeError
from typing import Optional

import httpx
from orcidlink.lib.config import config
from orcidlink.lib.responses import ErrorException, ErrorResponse
from orcidlink.model import ORCIDAuth
from pydantic import BaseModel


class AuthorizeParams(BaseModel):
    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    prompt: str
    state: str


def orcid_api_url(path):
    return f"{config().orcid.apiBaseURL}/{path}"


class ORCIDClientBase:
    def __init__(self, url: Optional[str] = None, access_token: Optional[str] = None):
        if url is None:
            raise TypeError('the "url" named parameter is required')
        self.base_url: str = url

        if access_token is None:
            raise TypeError('the "access_token" named parameter is required')
        self.access_token: str = access_token

    def url(self, path) -> str:
        return f"{self.base_url}/{path}"

    def header(self) -> dict:
        return {
            "Accept": "application/vnd.orcid+json",
            "Content-Type": "application/vnd.orcid+json",
            "Authorization": f"Bearer {self.access_token}",
        }

    @staticmethod
    def make_exception(response: httpx.Response, source: str) -> ErrorException:
        data = {
            "source": source,
            "originalStatusCode": response.status_code,
        }
        try:
            json_response = json.loads(response.text)
            # Remove potentially revealing information
            # TODO: send note to the ORCID folks asking them to omit the
            # token from the error response.
            if response.status_code == 401 or response.status_code == 403:
                if "error_description" in json_response:
                    del json_response["error_description"]
            data["originalResponseJSON"] = json_response
        except JSONDecodeError:
            data["originalResponseText"] = response.text

        return ErrorException(
            error=ErrorResponse(
                code="upstreamError",
                title="Error",
                message="Error fetching data from ORCID Auth api",
                data=data,
            ),
            status_code=400,
        )


class ORCIDAPIClient(ORCIDClientBase):
    #
    # Profile
    #
    def get_profile(self, orcid_id: str) -> dict:
        """
        Get the ORCID profile for the user associated with the orcid_id.

        The ORCID profile is massive and verbose, so we have not (yet?)
        modeled it, so we return the dict resulting from the json parse.
        Thus access to the profile should be through the get_json function,
        which can readily dig into the resulting dict.
        """
        response = httpx.get(self.url(f"{orcid_id}/record"), headers=self.header())
        return json.loads(response.text)

    def get_email(self, orcid_id: str) -> dict:
        response = httpx.get(self.url(f"{orcid_id}/email"), headers=self.header())
        return json.loads(response.text)

    #
    # Works
    #

    # TODO: do we want to type the raw works record?
    def get_works(self, orcid_id: str) -> dict:
        # TODO: catch errors here
        response = httpx.get(self.url(f"{orcid_id}/works"), headers=self.header())

        if response.status_code != 200:
            raise self.make_exception(response, source="get_works")

        return json.loads(response.text)

    def get_work(self, orcid_id: str, put_code: int) -> dict:
        # TODO: catch errors here
        url = self.url(f"{orcid_id}/works/{put_code}")
        response = httpx.get(url, headers=self.header())

        if response.status_code != 200:
            raise self.make_exception(response, source="get_works")

        return json.loads(response.text)

    def save_work(self, orcid_id: str, put_code: int, work_record: dict):
        response = httpx.put(
            self.url(f"{orcid_id}/work/{put_code}"),
            headers=self.header(),
            content=json.dumps(work_record),
        )

        if response.status_code != 200:
            raise self.make_exception(response, source="save_work")

        return json.loads(response.text)


class ORCIDOAuthClient(ORCIDClientBase):
    #
    # Revoke ORCID side of link.
    #
    def revoke_token(self):
        header = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": config().orcid.clientId,
            "client_secret": config().orcid.clientSecret,
            "token": self.access_token,
        }
        # TODO: determine all possible ORCID errors here, or the
        # pattern with which we can return useful info
        response = httpx.post(self.url("revoke"), headers=header, data=data)

        if response.status_code != 200:
            raise self.make_exception(response, source="revoke_link")

    def exchange_code_for_token(self, code: str):
        #
        # Exchange the temporary token from ORCID for the authorized token.
        #
        # ORCID does not specifically document this, but refers to the OAuth spec:
        # https://datatracker.ietf.org/doc/html/rfc8693.
        # Error structure defined here:
        # https://www.rfc-editor.org/rfc/rfc6749#section-5.2
        #
        header = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }
        # Note that the redirect uri below is just for the api - it is not actually used
        # for redirection in this case.
        # TODO: investigate and point to the docs, because this is weird.
        # TODO: put in orcid client!
        data = {
            "client_id": config().orcid.clientId,
            "client_secret": config().orcid.clientSecret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{config().services.ORCIDLink.url}/linking-sessions/oauth/continue",
        }
        response = httpx.post(
            f"{config().orcid.oauthBaseURL}/token", headers=header, data=data
        )
        json_response = json.loads(response.text)
        # TODO: branch on error
        return ORCIDAuth.parse_obj(json_response)


def orcid_api(token: str) -> ORCIDAPIClient:
    """
    Creates an instance of ORCIDAPIClient for accessing the ORCID REST API.

    This API provides all interactions we support with ORCID on behalf of a user, other
    than OAuth flow and OAuth/Auth interactions below.
    """
    return ORCIDAPIClient(url=config().orcid.apiBaseURL, access_token=token)


def orcid_oauth(token: str) -> ORCIDOAuthClient:
    """
    Creates an instance of ORCIDOAuthClient for support of the ORCID OAuth API.

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthClient(url=config().orcid.oauthBaseURL, access_token=token)
