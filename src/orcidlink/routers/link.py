from typing import Optional

from fastapi import APIRouter, Response
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    ErrorResponse,
    STD_RESPONSES,
    ensure_authorization,
    error_response,
    error_response_not_found,
    success_response_no_data,
)
from orcidlink.model import LinkRecord, LinkRecordPublic, ORCIDAuthPublic
from orcidlink.service_clients.ORCIDClient import orcid_oauth
from orcidlink.storage.storage_model import storage_model

router = APIRouter(prefix="/link")


def get_link_record(username: str) -> Optional[LinkRecord]:
    model = storage_model()
    return model.get_link_record(username)


@router.get(
    "",
    response_model=LinkRecordPublic,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {
            "description": "Link not available for this user",
            "model": ErrorResponse,
        },
        200: {
            "description": "Returns the <a href='#user-content-glossary_term_public-link-record'>Public link record</a> "
            + "for this user; contains no secrets",
            "model": LinkRecordPublic,
        },
    },
)
async def link(authorization: str | None = AUTHORIZATION_HEADER):
    """
    Get ORCID Link

    Return the link for the user associated with the KBase auth token passed in the "Authorization" header
    """
    _, token_info = ensure_authorization(authorization)

    link_record = get_link_record(token_info.user)

    if link_record is None:
        return error_response(
            "notFound",
            "Not Linked",
            "No link record was found for this user",
            status_code=404,
        )

    return LinkRecordPublic(
        username=link_record.username,
        created_at=link_record.created_at,
        expires_at=link_record.expires_at,
        orcid_auth=ORCIDAuthPublic(
            name=link_record.orcid_auth.name,
            scope=link_record.orcid_auth.scope,
            expires_in=link_record.orcid_auth.expires_in,
            orcid=link_record.orcid_auth.orcid,
        ),
    )


@router.get(
    "/is_linked",
    response_model=bool,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": "Returns a boolean indicating whether the user account is linked to ORCID",
            "model": bool,
        },
    },
)
async def is_linked(authorization: str | None = AUTHORIZATION_HEADER) -> bool:
    """
    Get whether Is Linked

    Determine if the user associated with the KBase auth token in the "Authorization" header has a
    link to an ORCID account.
    """
    _, token_info = ensure_authorization(authorization)
    link_record = get_link_record(token_info.user)
    return link_record is not None


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
            "model": ErrorResponse,
        },
    },
)
async def delete_link(authorization: str | None = AUTHORIZATION_HEADER):
    """
    Delete ORCID Link

    Removes the link for the user associated with the KBase auth token passed in the "Authorization" header
    """

    _, token_info = ensure_authorization(authorization)
    username = token_info.user
    link_record = get_link_record(username)

    if link_record is None:
        return error_response_not_found("User does not have an ORCID Link")

    # TODO: handle error? or propagate?
    orcid_oauth(link_record.orcid_auth.access_token).revoke_token()

    model = storage_model()

    # TODO: handle error? or propagate?
    model.delete_link_record(username)

    return success_response_no_data()
