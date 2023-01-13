import json
from json import JSONDecodeError

import httpx
from orcidlink.lib.config import config
from orcidlink.lib.responses import ErrorException, ErrorResponse
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
    def __init__(self, url: str = None, access_token: str = None):
        if url is None:
            raise TypeError('the "url" named parameter is required')
        self.base_url = url

        if access_token is None:
            raise TypeError('the "access_token" named parameter is required')
        self.access_token = access_token

    def url(self, path):
        return f"{self.base_url}/{path}"

    def header(self):
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
                if 'error_description' in json_response:
                    del json_response['error_description']
            data['originalResponseJSON'] = json_response
        except JSONDecodeError:
            data['originalResponseText'] = response.text

        return ErrorException(
            error=ErrorResponse(
                code="upstreamError",
                title="Error",
                message="Error fetching data from ORCID Auth api",
                data=data
            ),
            status_code=400
        )


class ORCIDAPIClient(ORCIDClientBase):
    #
    # Profile
    # 
    def get_profile(self, orcid_id: str):
        """
        Get the ORCID profile for the user associated with the orcid_id.

        The ORCID profile is massive and verbose, so we have not (yet?) 
        modeled it, so we return the dict resulting from the json parse. 
        Thus access to the profile should be through the get_json function, 
        which can readily dig into the resulting dict.
        """
        response = httpx.get(self.url(f"{orcid_id}/record"), headers=self.header())
        return json.loads(response.text)

    def get_email(self, orcid_id: str):
        response = httpx.get(self.url(f"{orcid_id}/email"), headers=self.header())
        return json.loads(response.text)

    #
    # Works
    #

    # TODO: do we want to type the raw works record?
    def get_works(self, orcid_id: str):
        # TODO: catch errors here
        response = httpx.get(self.url(f"{orcid_id}/works"), headers=self.header())

        if response.status_code != 200:
            raise self.make_exception(response, source="get_works")

        return json.loads(response.text)

    def get_work(self, orcid_id: str, put_code: str):
        # TODO: catch errors here
        url = self.url(f"{orcid_id}/works/{put_code}")
        response = httpx.get(url, headers=self.header())

        if response.status_code != 200:
            raise self.make_exception(response, source="get_works")

        return json.loads(response.text)

    def save_work(self, orcid_id: str, put_code: str, work_record: dict):
        response = httpx.put(self.url(f"{orcid_id}/work/{put_code}"),
                             headers=self.header(),
                             content=json.dumps(work_record))

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
            "client_id": config().module.CLIENT_ID,
            "client_secret": config().module.CLIENT_SECRET,
            "token": self.access_token,
        }
        # TODO: determine all possible ORCID errors here, or the
        # pattern with which we can return useful info
        response = httpx.post(self.url("revoke"), headers=header, data=data)

        if response.status_code != 200:
            raise self.make_exception(response, source="revoke_link")


def orcid_api(token: str) -> ORCIDAPIClient:
    """
    Creates an instance of ORCIDAPIClient for accessing the ORCID REST API.

    This API provides all interactions we support with ORCID on behalf of a user, other
    than OAuth flow and OAuth/Auth interactions below.
    """
    return ORCIDAPIClient(
        url=config().orcid.apiBaseURL,
        access_token=token
    )


def orcid_oauth(token: str) -> ORCIDOAuthClient:
    """
    Creates an instance of ORCIDOAuthClient for support of the ORCID OAuth API.

    This not for support of OAuth flow, but rather interactions with ORCID OAuth or
    simply Auth services.
    """
    return ORCIDOAuthClient(
        url=config().orcid.oauthBaseURL,
        access_token=token
    )
