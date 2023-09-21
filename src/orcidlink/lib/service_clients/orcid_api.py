import json
from typing import (
    Any,
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
from multidict import CIMultiDict
from pydantic import Field

from orcidlink.lib import exceptions
from orcidlink.lib.service_clients.orcid_common import (
    APIResponseError,
    ORCIDAPIError,
    ORCIDStringValue,
)
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.runtime import config


class ORCIDIdentifier(ServiceBaseModel):
    uri: str = Field(...)
    path: str = Field(...)
    host: str = Field(...)


class ORCIDIntValue(ServiceBaseModel):
    value: int = Field(...)


class Date(ServiceBaseModel):
    year: ORCIDStringValue = Field(...)
    month: Optional[ORCIDStringValue] = Field(default=None)
    day: Optional[ORCIDStringValue] = Field(default=None)


Visibility: TypeAlias = Literal["public", "limited", "private"]


class ORCIDPersonName(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(
        validation_alias="created-date", serialization_alias="created-date"
    )
    given_names: ORCIDStringValue = Field(
        validation_alias="given-names", serialization_alias="given-names"
    )
    family_name: Optional[ORCIDStringValue] = Field(
        default=None, validation_alias="family-name", serialization_alias="family-name"
    )
    credit_name: Optional[ORCIDStringValue] = Field(
        default=None, validation_alias="credit-name", serialization_alias="credit-name"
    )
    source: Optional[ORCIDStringValue] = Field(default=None)
    visibility: Visibility = Field(...)
    path: str = Field(...)
    # optional
    last_modified_date: ORCIDIntValue = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )


class ORCIDOtherNames(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(default=None)
    other_name: List[str] = Field(
        validation_alias="other-name", serialization_alias="other-name"
    )
    path: str = Field(...)


class ORCIDBiography(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(
        validation_alias="created-date", serialization_alias="created-date"
    )
    last_modified_date: ORCIDIntValue = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )
    content: str = Field(...)
    visibility: Visibility = Field(...)
    path: str = Field(...)


class ResearcherURLs(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )
    researcher_url: List[str] = Field(
        validation_alias="researcher-url", serialization_alias="researcher-url"
    )
    path: str = Field(...)


class ORCIDSource(ServiceBaseModel):
    source_orcid: Optional[ORCIDIdentifier] = Field(
        default=None,
        validation_alias="source-orcid",
        serialization_alias="source-orcid",
    )
    source_client_id: Optional[ORCIDIdentifier] = Field(
        default=None,
        validation_alias="source-client-id",
        serialization_alias="source-client-id",
    )
    source_name: Optional[ORCIDStringValue] = Field(
        default=None, validation_alias="source-name", serialization_alias="source-name"
    )
    assertion_origin_orcid: Optional[ORCIDStringValue] = Field(
        default=None,
        validation_alias="assertion-origin-orcid",
        serialization_alias="assertion-origin-orcid",
    )
    assertion_origin_client_id: Optional[ORCIDStringValue] = Field(
        default=None,
        validation_alias="assertion-origin-client-id",
        serialization_alias="assertion-origin-client-id",
    )
    assertion_origin_name: Optional[ORCIDStringValue] = Field(
        default=None,
        validation_alias="assertion-origin-name",
        serialization_alias="assertion-origin-name",
    )
    # just null in my record
    # assertion_origin_orcid
    # assertion_origin_client_id
    # assertion_origin_name


class ORCIDEmail(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(
        validation_alias="created-date", serialization_alias="created-date"
    )
    last_modified_date: ORCIDIntValue = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )
    source: ORCIDSource = Field(...)
    email: str = Field(...)
    path: Optional[str] = Field(default=None)
    visibility: Visibility = Field(...)
    verified: bool = Field(...)
    primary: bool = Field(...)
    put_code: Optional[int] = Field(
        default=None, validation_alias="put-code", serialization_alias="put-code"
    )


class ORCIDEmails(ServiceBaseModel):
    email: List[ORCIDEmail] = Field(...)
    path: str = Field(...)
    # optional - not populated when profile first created?
    last_modified_date: ORCIDIntValue | None = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )


class ORCIDPerson(ServiceBaseModel):
    name: ORCIDPersonName | None = Field(default=None)
    other_names: ORCIDOtherNames = Field(
        validation_alias="other-names", serialization_alias="other-names"
    )
    biography: ORCIDBiography | None = Field(default=None)
    researcher_urls: ResearcherURLs = Field(
        validation_alias="researcher-urls", serialization_alias="researcher-urls"
    )
    emails: ORCIDEmails | None = Field(default=None)
    # addresses: ORCIDAddresses
    # keywords
    # external_identifiers
    path: str = Field(...)
    # optional
    last_modified_date: ORCIDIntValue | None = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )


class ExternalIdNormalized(ServiceBaseModel):
    value: str = Field(...)
    transient: bool = Field(...)


class ExternalIdNormalizedError(ServiceBaseModel):
    error_code: str = Field(
        validation_alias="error-code", serialization_alias="error-code"
    )
    error_message: str = Field(
        validation_alias="error-message", serialization_alias="error-message"
    )
    transient: bool = Field(...)


class ExternalId(ServiceBaseModel):
    external_id_type: str = Field(
        validation_alias="external-id-type", serialization_alias="external-id-type"
    )
    external_id_value: str = Field(
        validation_alias="external-id-value", serialization_alias="external-id-value"
    )
    # TODO: this is a case of a field which is present when fetching, but
    # not saving - so this type should probably be forked int read & write versions
    external_id_normalized: Optional[ExternalIdNormalized] = Field(
        default=None,
        validation_alias="external-id-normalized",
        serialization_alias="external-id-normalized",
    )
    external_id_normalized_error: Optional[ExternalIdNormalizedError] = Field(
        default=None,
        validation_alias="external-id-normalized-error",
        serialization_alias="external-id-normalized-error",
    )
    external_id_url: ORCIDStringValue = Field(
        validation_alias="external-id-url", serialization_alias="external-id-url"
    )
    external_id_relationship: str = Field(
        validation_alias="external-id-relationship",
        serialization_alias="external-id-relationship",
    )


class ExternalIds(ServiceBaseModel):
    external_id: List[ExternalId] = Field(
        validation_alias="external-id", serialization_alias="external-id"
    )


class Title(ServiceBaseModel):
    title: ORCIDStringValue = Field(...)
    # subTitle: Optional
    # translated_title


class Citation(ServiceBaseModel):
    citation_type: str = Field(
        validation_alias="citation-type", serialization_alias="citation-type"
    )
    citation_value: str = Field(
        validation_alias="citation-value", serialization_alias="citation-value"
    )


class ContributorORCID(ServiceBaseModel):
    uri: Optional[str] = Field(default=None)
    path: Optional[str] = Field(default=None)
    host: Optional[str] = Field(default=None)


class ContributorAttributes(ServiceBaseModel):
    # TODO: this does not seem used either (always null), need to look up
    # the type.
    contributor_sequence: Optional[str] = Field(
        default=None,
        validation_alias="contributor-sequence",
        serialization_alias="contributor-sequence",
    )
    contributor_role: str = Field(
        validation_alias="contributor-role", serialization_alias="contributor-role"
    )


class Contributor(ServiceBaseModel):
    contributor_orcid: ContributorORCID = Field(
        validation_alias="contributor-orcid", serialization_alias="contributor-orcid"
    )
    # TODO: is this optional?
    credit_name: ORCIDStringValue = Field(
        validation_alias="credit-name", serialization_alias="credit-name"
    )
    # TODO: email is not exposed in the web ui, so I don't yet know
    # what the type really is
    contributor_email: Optional[str] = Field(
        default=None,
        validation_alias="contributor-email",
        serialization_alias="contributor-email",
    )
    contributor_attributes: ContributorAttributes = Field(
        validation_alias="contributor-attributes",
        serialization_alias="contributor-attributes",
    )


class ContributorWrapper(ServiceBaseModel):
    contributor: List[Contributor] = Field(...)


class WorkBase(ServiceBaseModel):
    type: str = Field(...)
    title: Title = Field(...)
    url: ORCIDStringValue = Field(...)
    publication_date: Date = Field(
        validation_alias="publication-date", serialization_alias="publication-date"
    )
    external_ids: ExternalIds = Field(
        validation_alias="external-ids", serialization_alias="external-ids"
    )


class NewWork(WorkBase):
    journal_title: ORCIDStringValue = Field(
        validation_alias="journal-title", serialization_alias="journal-title"
    )
    short_description: str = Field(
        validation_alias="short-description", serialization_alias="short-description"
    )
    citation: Citation = Field(...)
    contributors: ContributorWrapper = Field(...)


class WorkUpdate(NewWork):
    put_code: int = Field(validation_alias="put-code", serialization_alias="put-code")


class PersistedWork(ServiceBaseModel):
    put_code: int = Field(validation_alias="put-code", serialization_alias="put-code")
    # citation:
    # contributors
    # country
    # haven't seen an actual value for this
    # language_code
    created_date: ORCIDIntValue = Field(
        validation_alias="created-date", serialization_alias="created-date"
    )
    last_modified_date: ORCIDIntValue | None = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )
    # TODO: either defaults to str, and overridden in the standalone to optional,
    # or defaults to optional, and becomes required for summary.
    path: Optional[str] = Field(default=None)
    # publication_date: Date = Field(validation_alias="publication-date",
    # serialization_alias="publication-date")
    source: ORCIDSource = Field(...)
    visibility: Visibility = Field(...)
    journal_title: Optional[ORCIDStringValue] = Field(
        default=None,
        validation_alias="journal-title",
        serialization_alias="journal-title",
    )


class Work(WorkBase, PersistedWork):
    """
    These only appear in the call to get a single work record.
    """

    short_description: Optional[str] = Field(
        default=None,
        validation_alias="short-description",
        serialization_alias="short-description",
    )
    citation: Optional[Citation] = Field(default=None)
    contributors: ContributorWrapper = Field(...)


class WorkSummary(WorkBase, PersistedWork):
    display_index: str = Field(
        validation_alias="display-index", serialization_alias="display-index"
    )
    path: str = Field(...)


class WorkGroup(ServiceBaseModel):
    last_modified_date: ORCIDIntValue = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )
    external_ids: ExternalIds = Field(
        validation_alias="external-ids", serialization_alias="external-ids"
    )
    work_summary: List[WorkSummary] = Field(
        validation_alias="work-summary", serialization_alias="work-summary"
    )


class Works(ServiceBaseModel):
    group: List[WorkGroup] = Field(...)
    path: str = Field(...)
    # optional
    last_modified_date: ORCIDIntValue | None = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )


class ORCIDOrganizationAddress(ServiceBaseModel):
    city: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)


class ORCIDDisambiguatedOrganization(ServiceBaseModel):
    disambiguated_organization_identifier: str = Field(
        validation_alias="disambiguated-organization-identifier",
        serialization_alias="disambiguated-organization-identifier",
    )
    disambiguation_source: str = Field(
        validation_alias="disambiguation-source",
        serialization_alias="disambiguation-source",
    )


class ORCIDOrganization(ServiceBaseModel):
    name: str = Field(...)
    address: ORCIDOrganizationAddress = Field(...)
    disambiguated_organization: Optional[ORCIDDisambiguatedOrganization] = Field(
        default=None,
        validation_alias="disambiguated-organization",
        serialization_alias="disambiguated-organization",
    )


class ORCIDEmploymentSummary(ServiceBaseModel):
    created_date: ORCIDIntValue = Field(
        validation_alias="created-date", serialization_alias="created-date"
    )
    last_modified_date: ORCIDIntValue = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )
    source: ORCIDSource
    put_code: int = Field(validation_alias="put-code", serialization_alias="put-code")
    department_name: str = Field(
        ..., validation_alias="department-name", serialization_alias="department-name"
    )
    role_title: str = Field(
        validation_alias="role-title", serialization_alias="role-title"
    )
    start_date: Date = Field(
        validation_alias="start-date", serialization_alias="start-date"
    )
    end_date: Optional[Date] = Field(
        default=None, validation_alias="end-date", serialization_alias="end-date"
    )
    organization: ORCIDOrganization = Field(...)
    url: Optional[ORCIDStringValue] = Field(default=None)
    external_ids: Optional[ExternalIds] = Field(
        default=None,
        validation_alias="external-ids",
        serialization_alias="external-ids",
    )
    display_index: str = Field(
        validation_alias="display-index", serialization_alias="display-index"
    )
    visibility: Visibility = Field(...)
    path: str = Field(...)


class ORCIDEmploymentSummaryWrapper(ServiceBaseModel):
    employment_summary: ORCIDEmploymentSummary = Field(
        validation_alias="employment-summary", serialization_alias="employment-summary"
    )


class ORCIDAffiliationGroup(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )
    external_ids: ExternalIds = Field(
        validation_alias="external-ids", serialization_alias="external-ids"
    )
    summaries: Tuple[ORCIDEmploymentSummaryWrapper] = Field(...)


class Affiliations(ServiceBaseModel):
    last_modified_date: Optional[ORCIDIntValue] = Field(
        validation_alias="last-modified-date", serialization_alias="last-modified-date"
    )
    affiliation_group: Union[
        ORCIDAffiliationGroup, List[ORCIDAffiliationGroup]
    ] = Field(
        validation_alias="affiliation-group", serialization_alias="affiliation-group"
    )
    path: str = Field(...)


class ORCIDActivitiesSummary(ServiceBaseModel):
    employments: Affiliations = Field(...)
    # We need to do these activites one by one, as they are somewhat complex
    # distinctions: Affiliations = Field(...)
    # educations: Affiliations = Field(...)
    # fundings
    # invited_positions
    # memberships
    # peer_reviews
    # research_sources
    # services
    # works: Works
    path: str = Field(...)
    last_modified_date: ORCIDIntValue | None = Field(
        default=None,
        validation_alias="last-modified-date",
        serialization_alias="last-modified-date",
    )


#
# ORCID Profile as provided by the ORCID API
# Note that only those fields used at the top level are
# implemented.
#


class ORCIDProfile(ServiceBaseModel):
    orcid_identifier: ORCIDIdentifier = Field(
        validation_alias="orcid-identifier", serialization_alias="orcid-identifier"
    )
    # preferences: Dict[str, str] = Field(...)
    # history: ORCIDHistory = Field(...)
    person: ORCIDPerson = Field(...)
    activities_summary: ORCIDActivitiesSummary = Field(
        ...,
        validation_alias="activities-summary",
        serialization_alias="activities-summary",
    )


class AuthorizeParams(ServiceBaseModel):
    client_id: str
    response_type: str
    scope: str
    redirect_uri: str
    prompt: str
    state: str


def orcid_api_url(path: str) -> str:
    return f"{config().orcid_api_base_url}/{path}"


DetailType = TypeVar("DetailType", bound=ServiceBaseModel)


# A wrapper for all orcid api errors, wrapping the one returned from ORCID.
class APIErrorWrapper(ServiceBaseModel, Generic[DetailType]):
    source: str = Field(...)
    status_code: int = Field(...)
    detail: DetailType = Field(...)
    # error: Optional[str] = Field(default=None)
    # error_description: Optional[str] = Field(default=None)
    # error_text: Optional[str] = Field(default=None)


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


async def handle_json_response(response: aiohttp.ClientResponse) -> Any:
    """
    Given a response from the ORCID OAuth service, as an aiohttp
    response object, extract and return JSON from the body, handling
    any erroneous conditions.
    """
    content_type_raw = response.headers.get("Content-Type")
    if content_type_raw is None:
        raise exceptions.UpstreamError("No content-type in response")

    content_type, _, _ = content_type_raw.partition(";")
    if content_type != "application/vnd.orcid+json":
        raise exceptions.UpstreamError(
            (
                "Expected JSON response (application/vnd.orcid+json), "
                f"got {content_type}"
            )
        )

    try:
        json_response = await response.json()
    except json.JSONDecodeError as jde:
        raise exceptions.JSONDecodeError(
            "Error decoding JSON response",
            exceptions.JSONDecodeErrorData(message=str(jde)),
        )

    return json_response


def extract_error(result: Any) -> ORCIDAPIError | APIResponseError | None:
    # Shoehorn the error code into the appropriate structure
    if not isinstance(result, dict):
        return None

    # We use sentinal keys to determine the probably error type. The pydantic
    # model validation will ensure that the error is actually the correct
    # shape.
    if "error" in result:
        return ORCIDAPIError.model_validate(result)
    elif "error-code" in result:
        return APIResponseError.model_validate(result)
    else:
        return None


class ORCIDAPIClient:
    base_url: str
    access_token: str
    """
    A client for interacting with ORCID on behalf of a user.

    The access_token is required here as it is always presented as a
    bearer token. Note that this is different than the OAuth API in which
    the tokens are used as "sender-constrained" tokens - that is they are always
    accompanied by the client id and password.

    See: https://oauth.net/2/access-tokens/
    """

    def __init__(self, url: Optional[str] = None, access_token: Optional[str] = None):
        if url is None:
            raise TypeError('the "url" named parameter is required')
        self.base_url: str = url

        if access_token is None:
            raise TypeError('the "access_token" named parameter is required')
        self.access_token: str = access_token

    def url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def header(self) -> CIMultiDict[str]:
        return CIMultiDict(
            [
                ("Accept", "application/vnd.orcid+json"),
                ("Content-Type", "application/vnd.orcid+json"),
                ("Authorization", f"Bearer {self.access_token}"),
            ]
        )

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

        Possible errors:

        - no token: 403 (text/html)
        - invalid token: 401 (error="")
            uses error structure: error, error_description
            aka ORCIDAPIError
        - valid token, not authorized for this account: 401 (error-code=9017)
            uses error structure: response-code: int, error-code: int,
            developer-message: str, user-message: str, more-info: str (url) aka
            APIResponseError

        I think ORCID has these backwards. 401 should be "unauthorized" - that is
        authorization is required but not provided; 403 should be "authorization
        required" - that is, the profile access requires authorization, it has been
        provided, and it is inadequate.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url(f"{orcid_id}/record"), headers=self.header()
            ) as response:
                result = await handle_json_response(response)
                if response.status == 200:
                    return ORCIDProfile.model_validate(result)

                # Shoehorn the error code into the appropriate structure
                error = extract_error(result)

                # 1. ORCID Id does not correspond to a user.
                if response.status == 404:
                    raise exceptions.NotFoundError("ORCID User Not Found")

                if response.status == 401:
                    if isinstance(error, ORCIDAPIError):
                        # We need to grok the error from the error id and description.
                        # The invalid_token eror covers several cases.
                        if error.error == "invalid_token":
                            # 2. The access_token is invalid. Assuming the access token
                            # is only provided by a stored access_token, and thus was
                            # originally issued by ORCID, the cause could be:
                            # 2.1. User has removed KBase as a Trusted Partner
                            # 2.2. Token has been invalidated adminstratively; e.g.
                            #      token leak
                            # 2.3. Token has expired (very unlikely, as they last 20yrs)
                            # 2.4. Client id or password has been revoked
                            raise exceptions.AuthorizationRequiredError(
                                "Not authorized for ORCID Access"
                            )
                    elif isinstance(error, APIResponseError):
                        if error.error_code == 9017:
                            # 3. access_code does not match requested account, there is
                            # nothing to do here other than inform the user.
                            #
                            # This should not occur under normal circumstances, as we
                            # currently only make profile calls from the orcid link
                            # ui, which is carried out under the orcid link owner.
                            raise exceptions.UnauthorizedError(
                                "Not authorized for access to this account"
                            )
                    else:
                        # Wow, some other type of error.
                        raise exceptions.AuthorizationRequiredError(
                            "Not authorized for ORCID Access"
                        )

                # This will capture any >=300 errors, which we just
                # in through as an internal error.
                # Remember, actual >= 500 errors will result in an exception
                # thrown or possibly trigger a json parse error above, as we
                # expect a valid response.
                # TODO: we need to make the new upstram error carry data
                # raise exceptions.UpstreamError()
                raise exceptions.make_upstream_error(
                    response.status, result, source="get_profile"
                )

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
                    raise exceptions.make_upstream_error(
                        response.status, result, source="get_works"
                    )

                return Works.model_validate(result)

    async def get_work(self, orcid_id: str, put_code: int) -> GetWorkResult:
        # TODO: catch errors here
        url = self.url(f"{orcid_id}/works/{put_code}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.header()) as response:
                result = await response.json()
                if response.status != 200:
                    raise exceptions.make_upstream_error(
                        response.status, result, source="get_work"
                    )

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
                    raise exceptions.make_upstream_error(
                        response.status, result, source="save_work"
                    )

                return Work.model_validate(result)


def orcid_api(token: str) -> ORCIDAPIClient:
    """
    Creates an instance of ORCIDAPIClient for accessing the ORCID REST API.

    This API provides all interactions we support with ORCID on behalf of a user, other
    than OAuth flow and OAuth/Auth interactions below.
    """
    return ORCIDAPIClient(url=config().orcid_api_base_url, access_token=token)
