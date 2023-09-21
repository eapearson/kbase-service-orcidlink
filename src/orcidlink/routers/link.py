"""
Core support for using an existing ORCID Link

An ORCID Link opens many doors for providing user tools utilize the ORCID Api, but
this module focuses on providing direct access to one's ORCID Link. Once created,
via the "linking_sessions" module, a link may be fetched or deleted. There is currently
nothing to change about a link.

The url prefix for all endpoints is /link, all endpoints require the Authorization
header containing either a KBase login token, and all endpoints return JSON or nothing.

To that end the following endpoints are provided:

* GET /link - returns link information (model.LinkRecordPublic) if a link is found
          associated with the user account associated with the given KBase token
* GET /link/is_linked - similar to /link, but just returns a boolean indicating whether
        a link exists or not
# DELETE /link - removes the link associated with the user account associated with the
        given KBase token, and revokes the ORCID token in the link. Returns nothing if
        successful.

"""

from fastapi import APIRouter, Path, Response
from starlette.responses import JSONResponse

from orcidlink import process
from orcidlink.lib import errors, exceptions
from orcidlink.lib.auth import ensure_authorization
from orcidlink.lib.responses import AUTH_RESPONSES, AUTHORIZATION_HEADER, STD_RESPONSES
from orcidlink.model import (
    LinkingRecordShared,
    LinkRecordPublic,
    LinkRecordPublicNonOwner,
    ORCIDAuthPublic,
    ORCIDAuthPublicNonOwner,
)
from orcidlink.process import delete_link

router = APIRouter(prefix="/link")


USERNAME_PARAM = Path(
    description="The username",
    # It is a uuid, whose string representation is 36 characters.
)

ORCID_ID_PARAM = Path(
    description="The orcid id",
    # It is a uuid, whose string representation is 36 characters.
)


@router.get(
    "",
    response_model=LinkRecordPublic,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {
            "description": "Link not available for this user",
            "model": errors.ErrorResponse,
        },
        200: {
            "description": (
                "Returns the <a href='#user-content-glossary_term_public-link-record'>"
                "Public link record</a> "
                "for this user; contains no secrets"
            ),
            "model": LinkRecordPublic,
        },
    },
)
async def get_link(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> LinkRecordPublic | JSONResponse:
    """
    Get ORCID Link

    Return the link for the user associated with the KBase auth token passed in
    the "Authorization" header
    """
    _, token_info = await ensure_authorization(authorization)

    link_record = await process.link_record_for_user(token_info.user)

    if link_record is None:
        raise exceptions.NotFoundError("No link record was found for this user")

    return LinkRecordPublic(
        username=link_record.username,
        created_at=link_record.created_at,
        expires_at=link_record.expires_at,
        retires_at=link_record.retires_at,
        orcid_auth=ORCIDAuthPublic(
            name=link_record.orcid_auth.name,
            scope=link_record.orcid_auth.scope,
            expires_in=link_record.orcid_auth.expires_in,
            orcid=link_record.orcid_auth.orcid,
        ),
    )


@router.get(
    "/for_orcid/{orcid_id}",
    response_model=LinkRecordPublicNonOwner,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {
            "description": "Link not available for this user",
            "model": errors.ErrorResponse,
        },
        200: {
            "description": (
                "Returns the "
                "<a href='#user-content-glossary_term_public-link-record'>"
                "Public link record</a> "
                "for this user; contains no secrets"
            ),
            "model": LinkRecordPublic,
        },
    },
)
async def get_link_for_orcid(
    orcid_id: str = ORCID_ID_PARAM,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> LinkRecordPublicNonOwner | JSONResponse:
    """
    Get ORCID Link for a given ORCID Id

    Return the link for the given orcid id, as long as the user associated with the
    KBase auth token passed in the "Authorization" header is also the
    """
    _, _ = await ensure_authorization(authorization)

    link_record = await process.link_record_for_orcid_id(orcid_id)

    if link_record is None:
        raise exceptions.NotFoundError("No link record was found for this user")

    result = LinkRecordPublicNonOwner(
        username=link_record.username,
        orcid_auth=ORCIDAuthPublicNonOwner(
            name=link_record.orcid_auth.name,
            orcid=link_record.orcid_auth.orcid,
        ),
    )
    return result


@router.get(
    "/is_linked",
    response_model=bool,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": (
                "Returns a boolean indicating whether the user account is "
                "linked to ORCID"
            ),
            "model": bool,
        },
    },
)
async def get_is_linked(authorization: str | None = AUTHORIZATION_HEADER) -> bool:
    """
    Get whether Is Linked

    Determine if the user associated with the KBase auth token in the "Authorization"
    header has a link to an ORCID account.
    """
    _, token_info = await ensure_authorization(authorization)
    link_record = await process.link_record_for_user(token_info.user)

    return link_record is not None


@router.get(
    "/is_orcid_linked/{orcid_id}",
    response_model=bool,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": (
                "Returns a boolean indicating whether the orcid id linked "
                "to a KBase account"
            ),
            "model": bool,
        },
    },
)
async def get_is_orcid_linked(
    orcid_id: str = ORCID_ID_PARAM, authorization: str | None = AUTHORIZATION_HEADER
) -> bool:
    """
    Get whether Is Linked

    Determine if the user associated with the KBase auth token in the "Authorization"
    header has a link to an ORCID account.
    """
    _, _ = await ensure_authorization(authorization)
    link_record = await process.link_record_for_orcid_id(orcid_id)

    return link_record is not None


@router.get(
    "/share/{username}",
    response_model=LinkingRecordShared,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": "Returns the shared portion of an ORCID Link record",
            "model": LinkingRecordShared,
        },
    },
)
async def link_share(
    username: str = USERNAME_PARAM, authorization: str | None = AUTHORIZATION_HEADER
) -> LinkingRecordShared:
    """
    Get whether Is Linked

    Determine if the user associated with the KBase auth token in the "Authorization"
    header has a link to an ORCID account.
    """
    await ensure_authorization(authorization)

    link_record = await process.link_record_for_user(username)

    if link_record is None:
        raise exceptions.NotFoundError("Link not found for user")

    # TODO: CRITICAL - check which fields have been shared; for now assume the id is,
    # and perhaps we want to make it always available to kbase users if linked,
    # even though the ui can offer more fine grained control?
    return LinkingRecordShared(orcidId=link_record.orcid_auth.orcid)


#
# Delete Link
#
@router.delete(
    "",
    response_class=Response,
    status_code=204,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        204: {"description": "Successfully deleted the link"},
        404: {
            "description": "Link not available for this user",
            "model": errors.ErrorResponse,
        },
    },
)
async def delete_link_impl(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> Response:
    """
    Delete ORCID Link

    Removes the link for the user associated with the KBase auth token passed in
    the "Authorization" header
    """

    _, token_info = await ensure_authorization(authorization)

    await delete_link(token_info.user)

    return Response(status_code=204)
