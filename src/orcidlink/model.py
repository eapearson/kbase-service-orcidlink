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

from typing import List, Optional, Union

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


class LinkingSessionInitial(ServiceBaseModel):
    session_id: str = Field(...)
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)


class LinkingSessionStarted(LinkingSessionInitial):
    return_link: str | None = Field(...)
    skip_prompt: str = Field(...)


class LinkingSessionComplete(LinkingSessionStarted):
    orcid_auth: ORCIDAuth = Field(...)


# TODO: maybe just a quick hack, but we use
# this concept of "public" vs "private" types.
# Public types are safe for exposing via the api.
class LinkingSessionCompletePublic(LinkingSessionStarted):
    orcid_auth: ORCIDAuthPublic = Field(...)


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
    module_name: str = Field(alias="module-name")
    description: str = Field(...)
    language: str = Field(...)


# API


class ORCIDWork(ServiceBaseModel):
    putCode: int = Field(...)
    createdAt: int = Field(...)
    updatedAt: int = Field(...)
    source: str = Field(...)
    title: str = Field(...)
    journal: Optional[str]
    date: str = Field(...)
    workType: str = Field(...)
    url: str = Field(...)
    externalIds: List[ExternalId] = Field(...)


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
    works: List[ORCIDWork] = Field(...)


class ORCIDAffiliation(ServiceBaseModel):
    name: str = Field(...)
    role: str = Field(...)
    startYear: str = Field(...)
    endYear: Union[str, None] = Field(default=None)


class ORCIDProfile(ServiceBaseModel):
    orcidId: str = Field(...)
    firstName: str = Field(...)
    lastName: str = Field(...)
    bio: str = Field(...)
    affiliations: List[ORCIDAffiliation] = Field(...)
    works: List[ORCIDWork] = Field(...)
    emailAddresses: List[str] = Field(...)


class NewWork(ServiceBaseModel):
    """
    Represents a work record that is going to be added to ORCID.
    """

    title: str = Field(...)
    journal: str = Field(...)
    date: str = Field(...)
    workType: str = Field(...)
    url: str = Field(...)
    externalIds: List[ExternalId] = Field(...)


class WorkUpdate(NewWork):
    """
    Represents a work record which has been fetched from ORCID, modified,
    and can be sent back to update the ORCID work record
    """

    putCode: int = Field(...)


class JSONDecodeErrorData(ServiceBaseModel):
    status_code: int = Field(alias="status-code")
    error: str = Field(...)


class UnknownError(ServiceBaseModel):
    exception: str = Field(...)
