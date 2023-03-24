"""
Contains the data model for the application

Most application types used by router implementation should be located here. This
essentially represents the data model for the application. This insulates us from
the vagaries of the upstream APIs, and provides a consistent system of types,
naming conventions, etc.

All types inherit from pydantic's BaseModel, meaning that they will have bidirectional
JSON support, auto-documentation, the opportunity for more detailed schemas and
documentation.

"""

from typing import Annotated, List, Literal, Optional, Union

from orcidlink.lib.type import ServiceBaseModel
from pydantic import Field


class SimpleSuccess(ServiceBaseModel):
    ok: bool = Field(...)


class ExternalId(ServiceBaseModel):
    type: str = Field(...)
    value: str = Field(...)
    url: str = Field(...)
    relationship: str = Field(...)


class ORCIDAuth(ServiceBaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    refresh_token: str = Field(...)
    expires_in: int = Field(...)
    scope: str = Field(...)
    name: str = Field(...)
    orcid: str = Field(...)
    id_token: str = Field(...)


class ORCIDAuthPublic(ServiceBaseModel):
    name: str = Field(...)
    scope: str = Field(...)
    expires_in: int = Field(...)
    orcid: str = Field(...)


# Linking session

# Used when a session is initially created.
# It contains the state info needed in order to
# properly evaluate the linking session interactions in the
# absence of the original UI.
# E.g. cannot rely on having the auth cookie available, so we
# store it.


class LinkingSessionBase(ServiceBaseModel):
    session_id: str = Field(...)
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)


class LinkingSessionInitial(LinkingSessionBase):
    kind: Literal["initial"]


class LinkingSessionStarted(LinkingSessionBase):
    kind: Literal["started"]
    return_link: str | None = Field(...)
    skip_prompt: str = Field(...)


class LinkingSessionComplete(LinkingSessionBase):
    kind: Literal["complete"]
    return_link: str | None = Field(...)
    skip_prompt: str = Field(...)
    orcid_auth: ORCIDAuth = Field(...)


LinkingSession = Annotated[
    Union[LinkingSessionInitial, LinkingSessionStarted, LinkingSessionComplete],
    Field(discriminator="kind"),
]


# TODO: maybe just a quick hack, but we use
# this concept of "public" vs "private" types.
# Public types are safe for exposing via the api.
class LinkingSessionCompletePublic(LinkingSessionBase):
    kind: Literal["complete"]
    return_link: str | None = Field(...)
    skip_prompt: str = Field(...)
    orcid_auth: ORCIDAuthPublic = Field(...)


# class LinkingSessionPublic(ServiceBaseModel):
#     __root__: Union[LinkingSessionInitial, LinkingSessionStarted, LinkingSessionCompletePublic]


LinkingSessionPublic = Annotated[
    Union[LinkingSessionInitial, LinkingSessionStarted, LinkingSessionCompletePublic],
    Field(discriminator="kind"),
]


class SessionInfo(ServiceBaseModel):
    session_id: str = Field(...)


# The Link itself


class LinkRecord(ServiceBaseModel):
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)
    orcid_auth: ORCIDAuth = Field(...)


class LinkRecordPublic(ServiceBaseModel):
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)
    orcid_auth: ORCIDAuthPublic = Field(...)


# Config


class ServiceDescription(ServiceBaseModel):
    name: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=5, max_length=100)
    version: str = Field(min_length=5, max_length=50)
    language: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=50, max_length=4000)


# API


class ORCIDCitation(ServiceBaseModel):
    type: str = Field(...)
    value: str = Field(...)


# class ORCIDContributorORCIDInfo(ServiceBaseModel):
#     uri: str = Field(...)
#     path: str = Field(...)
#     # omitting host, seems never used


ContributorRole = str


class ORCIDContributor(ServiceBaseModel):
    orcidId: Optional[str] = Field(default=None)
    # orcidInfo: Optional[ORCIDContributorORCIDInfo] = Field(default=None)
    # orcidId: Optional[]
    name: str = Field(...)
    # omitting email, as it seems never used
    roles: List[ContributorRole] = Field(...)


class ORCIDContributorSelf(ServiceBaseModel):
    orcidId: str = Field(...)
    # orcidId: Optional[]
    name: str = Field(...)
    # omitting email, as it seems never used
    roles: List[ContributorRole] = Field(...)


class WorkBase(ServiceBaseModel):
    """
    Represents the core of a work record, both one persisted to ORCID
    as well as one which only exists in memory, full work record and
    summary.
    """

    title: str = Field(...)
    date: str = Field(...)
    workType: str = Field(...)
    url: str = Field(...)
    doi: str = Field(...)
    externalIds: List[ExternalId] = Field(...)
    # TODO: is really optional? check out the schema


class FullWork(WorkBase):
    journal: str = Field(...)
    shortDescription: str = Field(...)
    citation: ORCIDCitation = Field(...)
    selfContributor: ORCIDContributorSelf = Field(...)
    otherContributors: List[ORCIDContributor] = Field(...)


class NewWork(FullWork):
    """
    Represents a work record that is going to be added to ORCID.
    """

    pass


class PersistedWorkBase(ServiceBaseModel):
    putCode: int = Field(...)


class PersistedWork(PersistedWorkBase):
    createdAt: int = Field(...)
    updatedAt: int = Field(...)
    source: str = Field(...)

    # journal: Optional[str] = Field(default=None)
    # shortDescription: Optional[str] = Field(default=None)
    # citation: Optional[ORCIDCitation] = Field(default=None)


class Work(FullWork, PersistedWork):
    pass


class WorkUpdate(FullWork, PersistedWorkBase):
    """
    Represents a work record which has been fetched from ORCID, modified,
    and can be sent back to update the ORCID work record
    """

    pass


# TODO: unify these work types; tricky part is that we require fields for creating
# our own work records which are optional for those created at ORCID.


class WorkSummary(WorkBase, PersistedWork):
    journal: Optional[str] = Field(default=None)

    # Note that these fields have equivalents for NewWork and WorkUpdate
    # for which they are required, since those types are for our usage of
    # works. WorkSummary and Work cover all ORCID work records, so loosen
    # these type definitions to be optional.
    # Unfortunately pydantic does not seem to allow overriding types.
    # Okay, solved (hopefully) by only working with KBase generated records,
    # which will be stricter; i.e. will always ensure that these fields
    # are populated.
    # journal: Optional[str] = Field(default=None)
    # shortDescription: Optional[str] = Field(default=None)
    # citation: Optional[ORCIDCitation] = Field(default=None)


# class ORCIDWork(ORCIDWorkSummary):
#     selfContributor: ORCIDContributorSelf = Field(...)
#     otherContributors: Optional[List[ORCIDContributor]] = Field(default=None)


# For some reason, a "work" can be composed of more than one
# work record, one of which is the "preferred". I don't yet
# know what makes a work record "preferred".
# There is a set of external ids for the group, which appears
# to be identical for each of the work records.
# We do need to model it correctly, but not quite sure
# how to interpret it...
class ORCIDWorkGroup(ServiceBaseModel):
    updatedAt: int = Field(...)
    externalIds: List[ExternalId] = Field(...)
    works: List[WorkSummary] = Field(...)


class ORCIDAffiliation(ServiceBaseModel):
    name: str = Field(...)
    role: str = Field(...)
    startYear: str = Field(...)
    endYear: Union[str, None] = Field(default=None)


class ORCIDProfile(ServiceBaseModel):
    orcidId: str = Field(...)
    firstName: str = Field(...)
    lastName: str = Field(...)
    creditName: Optional[str] = Field(default=None)
    bio: str = Field(...)
    distinctions: List[ORCIDAffiliation] = Field(...)
    education: List[ORCIDAffiliation] = Field(...)
    employment: List[ORCIDAffiliation] = Field(...)
    # omit works since it is covered separately, and is somewhat
    # complicated...
    # works: List[WorkSummary] = Field(...)
    emailAddresses: List[str] = Field(...)


class JSONDecodeErrorData(ServiceBaseModel):
    status_code: int = Field(alias="status-code")
    error: str = Field(...)


class UnknownError(ServiceBaseModel):
    exception: str = Field(...)
