import json
from json import JSONDecodeError
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeAlias,
    TypeVar,
    Union,
)

# import httpx
import aiohttp
from pydantic import Field

from orcidlink import model
from orcidlink.lib import errors
from orcidlink.lib.config import config
from orcidlink.lib.type import ServiceBaseModel


class ORCIDIdentifier(ServiceBaseModel):
    uri: str = Field(...)
    path: str = Field(...)
    host: str = Field(...)


class ORCIDIntValue(ServiceBaseModel):
    value: int = Field(...)


class StringValue(ServiceBaseModel):
    value: str = Field(...)


class Date(ServiceBaseModel):
    year: StringValue = Field(...)
    month: Optional[StringValue] = Field(default=None)
    day: Optional[StringValue] = Field(default=None)


Visibility: TypeAlias = Literal["public", "limited", "private"]


class ORCIDPersonName(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(alias="created-date")
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    given_names: StringValue = Field(alias="given-names")
    family_name: StringValue = Field(alias="family-name")
    credit_name: Optional[StringValue] = Field(default=None, alias="credit-name")
    source: Optional[StringValue] = Field(default=None)
    visibility: Visibility = Field(...)
    path: str = Field(...)


class ORCIDOtherNames(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(default=None)
    other_name: List[str] = Field(alias="other-name")
    path: str = Field(...)


class ORCIDBiography(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(alias="created-date")
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    content: str = Field(...)
    visibility: Visibility = Field(...)
    path: str = Field(...)


class ResearcherURLs(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(
        default=None, alias="last-modified-date"
    )
    researcher_url: List[str] = Field(alias="researcher-url")
    path: str = Field(...)


class ORCIDSource(ServiceBaseModel):
    source_orcid: Optional[ORCIDIdentifier] = Field(default=None, alias="source-orcid")
    source_client_id: Optional[ORCIDIdentifier] = Field(
        default=None, alias="source-client-id"
    )
    source_name: StringValue = Field(alias="source-name")
    # just null in my record
    # assertion_origin_orcid
    # assertion_origin_client_id
    # assertion_origin_name


class ORCIDEmail(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(alias="created-date")
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    source: ORCIDSource = Field(...)
    email: str = Field(...)
    path: Optional[str] = Field(default=None)
    visibility: Visibility = Field(...)
    verified: bool = Field(...)
    primary: bool = Field(...)
    put_code: Optional[int] = Field(default=None, alias="put-code")


class ORCIDEmails(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    email: List[ORCIDEmail] = Field(...)
    path: str = Field(...)


class ORCIDPerson(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    name: ORCIDPersonName = Field(...)
    other_names: ORCIDOtherNames = Field(..., alias="other-names")
    biography: ORCIDBiography
    researcher_urls: ResearcherURLs = Field(alias="researcher-urls")
    emails: ORCIDEmails
    # addresses: ORCIDAddresses
    # keywords
    # external_identifiers
    path: str = Field(...)


class ExternalIdNormalized(ServiceBaseModel):
    value: str = Field(...)
    transient: bool = Field(...)


class ExternalIdNormalizedError(ServiceBaseModel):
    error_code: str = Field(..., alias="error-code")
    error_message: str = Field(..., alias="error-message")
    transient: bool = Field(...)


class ExternalId(ServiceBaseModel):
    external_id_type: str = Field(alias="external-id-type")
    external_id_value: str = Field(alias="external-id-value")
    # TODO: this is a case of a field which is present when fetching, but
    # not saving - so this type should probably be forked int read & write versions
    external_id_normalized: Optional[ExternalIdNormalized] = Field(
        default=None, alias="external-id-normalized"
    )
    external_id_normalized_error: Optional[ExternalIdNormalizedError] = Field(
        default=None, alias="external-id-normalized-error"
    )
    external_id_url: StringValue = Field(alias="external-id-url")
    external_id_relationship: str = Field(alias="external-id-relationship")


class ExternalIds(ServiceBaseModel):
    external_id: List[ExternalId] = Field(alias="external-id")


class Title(ServiceBaseModel):
    title: StringValue = Field(...)
    # subTitle: Optional
    # translated_title


class Citation(ServiceBaseModel):
    citation_type: str = Field(alias="citation-type")
    citation_value: str = Field(alias="citation-value")


class ContributorORCID(ServiceBaseModel):
    uri: Optional[str] = Field(default=None)
    path: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)


class ContributorAttributes(ServiceBaseModel):
    # TODO: this does not seem used either (always null), need to look up
    # the type.
    contributor_sequence: Optional[str] = Field(
        default=None, alias="contributor-sequence"
    )
    contributor_role: str = Field(alias="contributor-role")


class Contributor(ServiceBaseModel):
    contributor_orcid: ContributorORCID = Field(alias="contributor-orcid")
    # TODO: is this optional?
    credit_name: StringValue = Field(alias="credit-name")
    # TODO: email is not exposed in the web ui, so I don't yet know
    # what the type really is
    contributor_email: Optional[str] = Field(default=None, alias="contributor-email")
    contributor_attributes: ContributorAttributes = Field(
        alias="contributor-attributes"
    )


class ContributorWrapper(ServiceBaseModel):
    contributor: List[Contributor] = Field(...)


class WorkBase(ServiceBaseModel):
    type: str = Field(...)
    title: Title = Field(...)
    url: StringValue = Field(...)
    publication_date: Date = Field(alias="publication-date")
    external_ids: ExternalIds = Field(alias="external-ids")


class NewWork(WorkBase):
    journal_title: StringValue = Field(alias="journal-title")
    short_description: str = Field(alias="short-description")
    citation: Citation = Field(...)
    contributors: ContributorWrapper = Field(...)


class WorkUpdate(NewWork):
    put_code: int = Field(alias="put-code")


class PersistedWork(ServiceBaseModel):
    put_code: int = Field(alias="put-code")
    # citation:
    # contributors
    # country
    # haven't seen an actual value for this
    # language_code
    created_date: ORCIDIntValue = Field(alias="created-date")
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    # TODO: either defaults to str, and overridden in the standalone to optional,
    # or defaults to optional, and becomes required for summary.
    path: Optional[str] = Field(default=None)
    # publication_date: Date = Field(alias="publication-date")
    source: ORCIDSource = Field(...)
    visibility: Visibility = Field(...)
    journal_title: Optional[StringValue] = Field(default=None, alias="journal-title")


class Work(WorkBase, PersistedWork):
    """
    These only appear in the call to get a single work record.
    """

    short_description: Optional[str] = Field(default=None, alias="short-description")
    citation: Optional[Citation] = Field(default=None)
    contributors: ContributorWrapper = Field(...)


class WorkSummary(WorkBase, PersistedWork):
    display_index: str = Field(alias="display-index")
    path: str = Field(...)


class WorkGroup(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    external_ids: ExternalIds = Field(alias="external-ids")
    work_summary: List[WorkSummary] = Field(alias="work-summary")


class Works(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    group: List[WorkGroup] = Field(...)
    path: str = Field(...)


class ORCIDOrganizationAddress(ServiceBaseModel):
    city: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)


class ORCIDDisambiguatedOrganization(ServiceBaseModel):
    disambiguated_organization_identifier: str = Field(
        alias="disambiguated-organization-identifier"
    )
    disambiguation_source: str = Field(alias="disambiguation-source")


class ORCIDOrganization(ServiceBaseModel):
    name: str = Field(...)
    address: ORCIDOrganizationAddress = Field(...)
    disambiguated_organization: ORCIDDisambiguatedOrganization = Field(
        alias="disambiguated-organization"
    )


class ORCIDEmploymentSummary(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(alias="created-date")
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    source: ORCIDSource
    put_code: int = Field(alias="put-code")
    department_name: str = Field(..., alias="department-name")
    role_title: str = Field(alias="role-title")
    start_date: Date = Field(alias="start-date")
    end_date: Optional[Date] = Field(default=None, alias="end-date")
    organization: ORCIDOrganization = Field(...)
    url: Optional[StringValue] = Field(default=None)
    external_ids: Optional[ExternalIds] = Field(default=None, alias="external-ids")
    display_index: str = Field(alias="display-index")
    visibility: Visibility = Field(...)
    path: str = Field(...)


class ORCIDEmploymentSummaryWrapper(ServiceBaseModel):
    employment_summary: ORCIDEmploymentSummary = Field(alias="employment-summary")


class ORCIDAffiliationGroup(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(
        default=None, alias="last-modified-date"
    )
    external_ids: ExternalIds = Field(alias="external-ids")
    summaries: Tuple[ORCIDEmploymentSummaryWrapper] = Field(...)


class Affiliations(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(alias="last-modified-date")
    affiliation_group: Union[
        ORCIDAffiliationGroup, List[ORCIDAffiliationGroup]
    ] = Field(alias="affiliation-group")
    path: str = Field(...)


class ORCIDActivitiesSummary(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(alias="last-modified-date")
    distinctions: Affiliations = Field(...)
    educations: Affiliations = Field(...)
    employments: Affiliations = Field(...)
    # fundings
    # invited_positions
    # memberships
    # peer_reviews
    # research_sources
    # services
    works: Works
    path: str = Field(...)


#
# ORCID Profile as provided by the ORCID API
# Note that only those fields used at the top level are
# implemented.
#


class ORCIDProfile(ServiceBaseModel):
    orcid_identifier: ORCIDIdentifier = Field(alias="orcid-identifier")
    # preferences: Dict[str, str] = Field(...)
    # history: ORCIDHistory = Field(...)
    person: ORCIDPerson = Field(...)
    activities_summary: ORCIDActivitiesSummary = Field(..., alias="activities-summary")


class AuthorizeParams(ServiceBaseModel):
    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    prompt: str
    state: str


def orcid_api_url(path: str) -> str:
    return f"{config().orcid.apiBaseURL}/{path}"


# This is the usual error response for 4xx
class APIResponseError(ServiceBaseModel):
    response_code: int = Field(alias="response-code")
    developer_message: str = Field(alias="developer-message")
    user_message: str = Field(alias="user-message")
    error_code: int = Field(alias="error-code")
    more_info: str = Field(alias="more-info")


# This is the usual error response for 500
class APIResponseInternalServerError(ServiceBaseModel):
    message_version: str = Field(alias="message-version")
    orcid_profile: Optional[Any] = Field(default=None, alias="orcid-profile")
    orcid_search_results: Optional[Any] = Field(
        default=None, alias="orcid-search-results"
    )
    error_desc: StringValue = Field(alias="error-desc")


# This is return for at least 401
class APIResponseUnauthorized(ServiceBaseModel):
    error: str = Field(...)
    error_description: Optional[str] = Field(default=None, alias="error-description")


class APIResponseUnknownError(ServiceBaseModel):
    detail: Any = Field(...)


class APIParseError(ServiceBaseModel):
    error_text: str = Field(alias="error-text")


DetailType = TypeVar("DetailType", bound=ServiceBaseModel)


# A wrapper for all orcid api errors, wrapping the one returned from ORCID.
class APIErrorWrapper(ServiceBaseModel, Generic[DetailType]):
    source: str = Field(...)
    status_code: int = Field(...)
    detail: DetailType = Field(...)
    # error: Optional[str] = Field(default=None)
    # error_description: Optional[str] = Field(default=None)
    # error_text: Optional[str] = Field(default=None)


def make_exception(
    status: int, json_response: Any, source: str
) -> errors.ServiceErrorX:
    if isinstance(json_response, dict):
        # Determine which of the 3 types of errors were returned, if we
        # do have a json_response (not all api endpoints have a response).
        if "error" in json_response:
            # Remove potentially revealing information
            # TODO: send note to the ORCID folks asking them to omit the
            # token from the error response.
            if status == 401 or status == 403:
                json_response.pop("error_description")

            return errors.UpstreamError(
                "Error fetching data from ORCID",
                data={
                    "source": source,
                    "status_code": status,
                    "detail": json_response,
                },
            )
        elif "message-version" in json_response:
            return errors.UpstreamError(
                "Error fetching data from ORCID",
                data={
                    "source": source,
                    "status_code": status,
                    "detail": json_response,
                },
            )
        elif "response-code" in json_response:
            return errors.UpstreamError(
                "Error fetching data from ORCID",
                data={
                    "source": source,
                    "status_code": status,
                    "detail": json_response,
                },
            )
    return errors.UpstreamError(
        "Error fetching data from ORCID",
        data={
            "source": source,
            "status_code": status,
            "detail": json_response,
        },
    )


class ORCIDClientBase:
    def __init__(self, url: Optional[str] = None, access_token: Optional[str] = None):
        if url is None:
            raise TypeError('the "url" named parameter is required')
        self.base_url: str = url

        if access_token is None:
            raise TypeError('the "access_token" named parameter is required')
        self.access_token: str = access_token

    def url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def header(self) -> Dict[str, str]:
        return {
            "Accept": "application/vnd.orcid+json",
            "Content-Type": "application/vnd.orcid+json",
            "Authorization": f"Bearer {self.access_token}",
        }


class GetEmailResult(ServiceBaseModel):
    email: ORCIDEmail


class WorkWrapper(ServiceBaseModel):
    work: Work


class NewWorkWrapper(ServiceBaseModel):
    work: NewWork


class GetWorkResult(ServiceBaseModel):
    bulk: Tuple[WorkWrapper]


class CreateWorkInput(ServiceBaseModel):
    bulk: Tuple[NewWorkWrapper]


class ORCIDAPIClient(ORCIDClientBase):
    #
    # Profile
    #
    async def get_profile(self, orcid_id: str) -> ORCIDProfile:
        """
        Get the ORCID profile for the user associated with the orcid_id.

        The ORCID profile is massive and verbose, so we have not (yet?)
        modeled it, so we return the dict resulting from the json parse.
        Thus access to the profile should be through the get_json function,
        which can readily dig into the resulting dict.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url(f"{orcid_id}/record"), headers=self.header()
            ) as response:
                result = await response.json()
                if response.status == 404:
                    raise errors.NotFoundError("ORCID user profile not found")
                elif response.status != 200:
                    # This will capture any < 500 errors, which we just
                    # in through as an internal error.
                    # Remember, actual >= 500 errors will result in an exception
                    # thrown or possibly trigger a json parse error above, as we
                    # expect a valid response.
                    raise make_exception(response.status, result, source="get_profile")
                    # raise errors.InternalError(
                    #     "Unknown error fetching ORCID user profile"
                    # )
                else:
                    return ORCIDProfile.model_validate(result)

    #
    # Works
    #

    # TODO: do we want to type the raw works record?
    async def get_works(self, orcid_id: str) -> Works:
        # TODO: catch errors here
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url(f"{orcid_id}/works"), headers=self.header()
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise make_exception(response.status, result, source="get_works")

                return Works.model_validate(result)

    async def get_work(self, orcid_id: str, put_code: int) -> GetWorkResult:
        # TODO: catch errors here
        url = self.url(f"{orcid_id}/works/{put_code}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.header()) as response:
                result = await response.json()
                if response.status != 200:
                    raise make_exception(response.status, result, source="get_work")

                # safe json decode
                # try:
                #     json_response = json.loads(response.text)
                # except JSONDecodeError as jde:
                #     raise errors.UpstreamError(
                #         "Error decoding the ORCID response as JSON",
                #         data={"exception": str(jde)},
                #     )

                return GetWorkResult.model_validate(result)

    async def save_work(
        self, orcid_id: str, put_code: int, work_record: WorkUpdate
    ) -> Work:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                self.url(f"{orcid_id}/work/{put_code}"),
                headers=self.header(),
                data=json.dumps(work_record.model_dump(by_alias=True)),
            ) as response:
                result = await response.json()
                if response.status != 200:
                    raise make_exception(response.status, result, source="save_work")

                return Work.model_validate(result)


class ORCIDAPIError(ServiceBaseModel):
    error: str = Field(...)
    error_description: str = Field(...)


class ORCIDOAuthClient(ORCIDClientBase):
    #
    # Revoke ORCID side of link.
    #
    async def revoke_token(self) -> None:
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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url("revoke"), headers=header, data=data
            ) as response:
                if response.status != 200:
                    raise make_exception(response.status, None, source="revoke_link")

    async def exchange_code_for_token(self, code: str) -> model.ORCIDAuth:
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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config().orcid.oauthBaseURL}/token", headers=header, data=data
            ) as response:
                content_type_raw = response.headers.get("Content-Type")
                if content_type_raw is None:
                    raise errors.UpstreamError("No content-type in response")

                content_type, _, _ = content_type_raw.partition(";")
                if content_type == "application/json":
                    try:
                        json_response = await response.json()
                    except JSONDecodeError as jde:
                        raise errors.UpstreamError(
                            "Error decoding JSON response"
                        ) from jde

                    if response.status == 200:
                        # TODO: branch on error
                        return model.ORCIDAuth.model_validate(json_response)
                    else:
                        print("ERROR!", response.text)

                        if "error" in json_response:
                            error = ORCIDAPIError.model_validate(json_response)
                            raise errors.UpstreamError(error.error_description)
                        else:
                            raise errors.UpstreamError(
                                "Unexpected Error Response from ORCID"
                            )
                else:
                    raise errors.UpstreamError(
                        f"Expected JSON response, got {content_type}"
                    )


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
