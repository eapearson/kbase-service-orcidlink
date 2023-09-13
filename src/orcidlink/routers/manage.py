from typing import Any, Dict, List, Optional, Union

import pymongo
from fastapi import APIRouter, Body, Path, Response, status
from fastapi.responses import JSONResponse
from pydantic import Field

from orcidlink.lib import exceptions
from orcidlink.lib.auth import ensure_account
from orcidlink.lib.responses import AUTH_RESPONSES, AUTHORIZATION_HEADER, STD_RESPONSES
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.model import (
    LinkingSessionComplete,
    LinkingSessionInitial,
    LinkingSessionStarted,
    LinkRecord,
)
from orcidlink.storage.storage_model import storage_model
from orcidlink.storage.storage_model_mongo import StatsRecord

router = APIRouter(prefix="/manage")


class IsManagerResponse(ServiceBaseModel):
    is_manager: bool = Field(...)


USERNAME_PARAM = Path(
    description="The username",
    # It is a uuid, whose string representation is 36 characters.
)


@router.get(
    "/is_manager",
    response_model=IsManagerResponse,
    tags=["manage"],
    responses={
        200: {
            "description": "Successfully returns the service status",
            "model": IsManagerResponse,
        }
    },
)
async def get_is_manager(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> IsManagerResponse:
    """
    TEST
    """
    _, account_info = await ensure_account(authorization)

    if "orcidlink_admin" not in account_info.customroles:
        return IsManagerResponse(is_manager=False)
        # raise exceptions.UnauthorizedError("Not authorized for management operations")

    return IsManagerResponse(is_manager=True)


class GetLinksResponse(ServiceBaseModel):
    links: List[LinkRecord]


class FilterByUsername(ServiceBaseModel):
    eq: Optional[str] = Field(default=None)
    contains: Optional[str] = Field(default=None)


class FilterByORCIDId(ServiceBaseModel):
    eq: str = Field(...)


class FilterByEpochTime(ServiceBaseModel):
    eq: Optional[int] = Field(default=None)
    gte: Optional[int] = Field(default=None)
    gt: Optional[int] = Field(default=None)
    lte: Optional[int] = Field(default=None)
    lt: Optional[int] = Field(default=None)


class FilterByCreationTime(FilterByEpochTime):
    pass


class FilterByExpirationTime(FilterByEpochTime):
    pass


class QueryFind(ServiceBaseModel):
    username: Optional[FilterByUsername] = Field(default=None)
    orcid: Optional[FilterByORCIDId] = Field(default=None)
    created: Optional[FilterByCreationTime] = Field(default=None)
    expires: Optional[FilterByExpirationTime] = Field(default=None)

    class Config:
        extra = "forbid"


class QuerySortSpec(ServiceBaseModel):
    field_name: str = Field(...)
    descending: Optional[bool] = Field(default=None)


class QuerySort(ServiceBaseModel):
    specs: List[QuerySortSpec] = Field(...)


class SearchQuery(ServiceBaseModel):
    find: Optional[QueryFind] = Field(default=None)
    sort: Optional[QuerySort] = Field(default=None)
    offset: Optional[int] = Field(default=None)
    limit: Optional[int] = Field(default=None)

    class Config:
        extra = "forbid"


SEARCH_QUERY = Body(
    Default=None,
    description="""A search expression by which to filter link records.
    """,
    model=SearchQuery,
)


def augment_with_time_filter(
    filter: Dict[str, Dict[str, Union[str, int]]],
    field_name: str,
    possible_filter: Optional[FilterByEpochTime],
) -> Any:
    """
    Given a
    """
    if possible_filter is None:
        return filter

    if possible_filter.eq is not None:
        filter[field_name] = {"$eq": possible_filter.eq}
    if possible_filter.gt is not None:
        filter[field_name] = {"$gt": possible_filter.gt}
    if possible_filter.gte is not None:
        filter[field_name] = {"$gte": possible_filter.gte}
    if possible_filter.lt is not None:
        filter[field_name] = {"$lt": possible_filter.lt}
    if possible_filter.lte is not None:
        filter[field_name] = {"$lte": possible_filter.lte}

    return filter


@router.post(
    "/links",
    response_model=GetLinksResponse,
    tags=["manage"],
    responses={
        200: {
            "description": "Successfully returns the service status",
            "model": GetLinksResponse,
        }
    },
)
async def get_links(
    authorization: str | None = AUTHORIZATION_HEADER,
    query: Optional[SearchQuery] = SEARCH_QUERY,
) -> GetLinksResponse:
    """
    TEST
    """
    _, account_info = await ensure_account(authorization)

    if "orcidlink_admin" not in account_info.customroles:
        raise exceptions.UnauthorizedError("Not authorized for management operations")

    filter: dict[str, dict[str, str | int]] = {}
    sort = []
    offset = 0
    limit = None
    if query:
        if query.find is not None:
            if query.find.username is not None:
                if query.find.username.eq is not None:
                    filter["username"] = {"$eq": query.find.username.eq}

            if query.find.orcid is not None:
                if query.find.orcid.eq is not None:
                    filter["orcid_auth.orcid"] = {"$eq": query.find.orcid.eq}

            augment_with_time_filter(filter, "created_at", query.find.created)
            augment_with_time_filter(filter, "expires_at", query.find.expires)

        if query.sort is not None:
            for sort_spec in query.sort.specs:
                sort.append(
                    (
                        sort_spec.field_name,
                        pymongo.DESCENDING
                        if sort_spec.descending is True
                        else pymongo.ASCENDING,
                    )
                )

        if query.offset is not None:
            offset = query.offset

        if query.limit is not None:
            # TODO: place reasonable limits on this
            limit = query.limit

    model = storage_model()
    links = await model.get_link_records(
        filter=filter, sort=sort, offset=offset, limit=limit
    )

    return GetLinksResponse(links=links)


@router.get(
    "/link/{username}",
    response_model=LinkRecord,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES
        # 404: {
        #     "description": "Link not available for this user",
        #     "model": errors.ErrorResponse,
        # },
        # 200: {
        #     "description": "Returns the <a href='#user-content-glossary_term_public-link-record'>Public link record</a> "
        #     + "for this user; contains no secrets",
        #     "model": LinkRecordPublic,
        # },
    },
)
async def get_link(
    username: str = USERNAME_PARAM,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> LinkRecord | JSONResponse:
    """
    Get ORCID Link

    Return the link for the user associated with the KBase auth token passed in
    the "Authorization" header
    """
    _, account_info = await ensure_account(authorization)

    if "orcidlink_admin" not in account_info.customroles:
        raise exceptions.UnauthorizedError("Not authorized for management operations")

    model = storage_model()
    link_record = await model.get_link_record(username)

    if link_record is None:
        raise exceptions.NotFoundError("No link record was found for this user")

    return link_record


class GetLinkingSessionsResponse(ServiceBaseModel):
    initial_linking_sessions: List[LinkingSessionInitial]
    started_linking_sessions: List[LinkingSessionStarted]
    completed_linking_sessions: List[LinkingSessionComplete]


@router.get(
    "/linking_sessions",
    response_model=GetLinkingSessionsResponse,
    tags=["manage"],
    responses={
        200: {
            "description": "Successfully returns the service status",
            "model": GetLinksResponse,
        }
    },
)
async def get_linking_sessions(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> GetLinkingSessionsResponse:
    """
    TEST
    """
    _, account_info = await ensure_account(authorization)

    if "orcidlink_admin" not in account_info.customroles:
        raise exceptions.UnauthorizedError("Not authorized for management operations")

    # print(account_info)
    model = storage_model()
    initial_linking_sessions = await model.get_linking_sessions_initial()
    started_linking_sessions = await model.get_linking_sessions_started()
    completed_linking_sessions = await model.get_linking_sessions_completed()

    return GetLinkingSessionsResponse(
        initial_linking_sessions=initial_linking_sessions,
        started_linking_sessions=started_linking_sessions,
        completed_linking_sessions=completed_linking_sessions,
    )


@router.delete(
    "/expired_linking_sessions",
    status_code=204,
    responses={
        204: {"description": "Successfully deleted expired sessions"},
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        # 403: {
        #     "description": "Username does not match linking session",
        #     "model": errors.ErrorResponse,
        # },
        # 404: {
        #     "description": "Linking session not found",
        #     "model": errors.ErrorResponse,
        # },
    },
    tags=["linking-sessions"],
)
async def delete_expired_linking_sessions(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> Response:
    """
    Delete Expired Linking Sessions
    """
    _, account_info = await ensure_account(authorization)
    if "orcidlink_admin" not in account_info.customroles:
        raise exceptions.UnauthorizedError("Not authorized for management operations")

    # session_record = await get_linking_session_completed(session_id, authorization)

    model = storage_model()
    await model.delete_expired_sesssions()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class GetStatsResponse(ServiceBaseModel):
    stats: StatsRecord


@router.get(
    "/stats",
    response_model=GetStatsResponse,
    tags=["manage"],
    responses={
        200: {
            "description": "Successfully returns overview stats for the service",
            "model": GetStatsResponse,
        }
    },
)
async def get_stats(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> GetStatsResponse:
    """
    TEST
    """
    _, account_info = await ensure_account(authorization)

    if "orcidlink_admin" not in account_info.customroles:
        raise exceptions.UnauthorizedError("Not authorized for management operations")

    model = storage_model()
    stats = await model.get_stats()

    return GetStatsResponse(stats=stats)
