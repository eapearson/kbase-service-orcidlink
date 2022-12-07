import json

import requests
from lib.config import get_config
from lib.responses import ErrorException, ErrorResponse
from pydantic import BaseModel


class AuthorizeParams(BaseModel):
    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    prompt: str
    state: str


def orcid_api_url(path):
    return f"{get_config(['orcid', 'apiBaseURL'])}/{path}"


class ORCIDAPI:
    def __init__(self, url: str, access_token: str):
        if url is None:
            raise TypeError('api_url is required to create an ORCID Client')
        self.base_url = url

        if access_token is None:
            raise TypeError('access_token is required to create an ORCID Client')
        self.access_token = access_token

    def url(self, path):
        return f"{self.base_url}/{path}"

    def header(self):
        return {
            "Accept": "application/vnd.orcid+json",
            "Content-Type": "application/vnd.orcid+json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def make_exception(self, response: requests.Response, source: str):
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
                del json_response['error_description']
            data['originalResponseJSON'] = json_response
        except Exception:
            data['originalResponseText'] = response.text

        return ErrorException(
            error=ErrorResponse(
                code="upstreamError",
                title="Error",
                message="Error fetching data from ORCID api",
                data=data
            ),
            status_code=400
        )

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
        response = requests.get(self.url(f"{orcid_id}/record"), headers=self.header())
        return json.loads(response.text)

    def get_email(self, orcid_id: str):
        response = requests.get(self.url(f"{orcid_id}/email"), headers=self.header())
        return json.loads(response.text)

    #
    # Works
    #

    # TODO: do we want to type the raw works record?
    def get_works(self, orcid_id: str):
        # TODO: catch errors here
        response = requests.get(self.url(f"{orcid_id}/works"), headers=self.header())

        if response.status_code != 200:
            raise self.make_exception(response, source="get_works")

        return json.loads(response.text)

    def save_work(self, orcid_id: str, put_code: str, work_record):
        response = requests.put(self.url(f"{orcid_id}/works/{put_code}"), headers=self.header(),
                                data=json.dumps(work_record))

        if response.status_code != 200:
            raise self.make_exception(response, source="save_work")

        return json.loads(response.text)


class ORCIDOAuth:
    def __init__(self, url: str, access_token: str):
        if url is None:
            raise TypeError('url is required to create an ORCID OAuth Client')
        self.base_url = url

        if access_token is None:
            raise TypeError('access_token is required to create an ORCID OAuth Client')
        self.access_token = access_token

    def url(self, path):
        return f"{self.base_url}/{path}"

    def header(self):
        return {
            "Accept": "application/vnd.orcid+json",
            "Content-Type": "application/vnd.orcid+json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def make_exception(self, response: requests.Response, source: str):
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
                del json_response['error_description']
            data['originalResponseJSON'] = json_response
        except Exception:
            data['originalResponseText'] = response.text

        return ErrorException(
            error=ErrorResponse(
                code="upstreamError",
                title="Error",
                message="Error fetching data from ORCID api",
                data=data
            ),
            status_code=400
        )

    #
    # Revoke ORCID side of link.
    #
    def revoke_token(self):
        header = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "client_id": get_config(["env", "CLIENT_ID"]),
            "client_secret": get_config(["env", "CLIENT_SECRET"]),
            "token": self.access_token,
        }
        # TODO: determine all possible ORCID errors here, or the
        # pattern with which we can return useful info
        response = requests.post(self.url("revoke"), headers=header, data=data)

        if response.status_code != 200:
            raise self.make_exception(response, source="revoke_link")


def orcid_api(token: str) -> ORCIDAPI:
    return ORCIDAPI(
        url=get_config(['orcid', 'apiBaseURL']),
        access_token=token
    )


def orcid_oauth(token: str) -> ORCIDOAuth:
    return ORCIDOAuth(
        url=get_config(['orcid', 'oauthBaseURL']),
        access_token=token
    )
