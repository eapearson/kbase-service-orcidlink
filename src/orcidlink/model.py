from typing import List, Optional, Union

from pydantic import BaseModel, Field


class SimpleSuccess(BaseModel):
    ok: bool = Field(...)


class ExternalId(BaseModel):
    type: str
    value: str
    url: str
    relationship: str


class ORCIDAuth(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(...)
    refresh_token: str = Field(...)
    expires_in: int = Field(...)
    scope: str = Field(...)
    name: str = Field(...)
    orcid: str = Field(...)
    id_token: str = Field(...)


class ORCIDAuthPublic(BaseModel):
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

type


class LinkingSessionInitial(BaseModel):
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


class SessionInfo(BaseModel):
    session_id: str = Field(...)


# The Link itself


class LinkRecord(BaseModel):
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)
    orcid_auth: ORCIDAuth


class LinkRecordPublic(BaseModel):
    username: str = Field(...)
    created_at: int = Field(...)
    expires_at: int = Field(...)
    orcid_auth: ORCIDAuthPublic


# Config


class ServiceDescription(BaseModel):
    module_name: str = Field(alias="module-name")
    description: str = Field(...)
    language: str = Field(...)


# API


class ORCIDWork(BaseModel):
    putCode: int = Field(...)
    createdAt: int = Field(...)
    updatedAt: int = Field(...)
    source: str = Field(...)
    title: str = Field(...)
    journal: Optional[str]
    date: str = Field(...)
    workType: str = Field(...)
    url: str = Field(...)
    externalIds: List[ExternalId]


class ORCIDAffiliation(BaseModel):
    name: str = Field(...)
    role: str = Field(...)
    startYear: str = Field(...)
    endYear: Union[str, None] = None


class ORCIDProfile(BaseModel):
    orcidId: str = Field(...)
    firstName: str = Field(...)
    lastName: str = Field(...)
    bio: str = Field(...)
    affiliations: List[ORCIDAffiliation]
    works: List[ORCIDWork]
    emailAddresses: List[str] = Field(...)
