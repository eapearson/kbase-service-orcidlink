from fastapi import APIRouter, Response
from lib.ORCIDClient import orcid_oauth
from lib.auth import get_username
from lib.responses import (ErrorResponse, ensure_authorization, error_response,
                           success_response_no_data)
from lib.storage_model import StorageModel
from model_types import (LinkRecordPublic, ORCIDAuthPublic)
from routers.works import get_link_record

from src.lib.route_utils import AUTHORIZATION_HEADER, AUTH_RESPONSES

################################
# API
################################


##
# /status - The status of the service.
#
# The utility of this endpoint is really as a lightweight call to ping the
# service.
# Also, most services and all KB-SDK apps have a /status endpoint.
# As a side benefit, it also returns non-private configuration.
# TODO: perhaps non-private configuration should be accessible via an
# "/info" endpoint.
#

router = APIRouter(prefix="/link", responses={404: {"description": "Not found"}})


#
# Link management
#

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
        204: {"description": "Successfully deleted the link"},
    }
)
async def delete_link(
        authorization: str | None = AUTHORIZATION_HEADER
):
    """
    Removes the link for the user associated with the KBase auth token passed in the "Authorization" header
    """

    authorization = ensure_authorization(authorization)
    username = get_username(authorization)
    link_record = get_link_record(username)

    if link_record is None:
        # idempotent, so don't throw error
        return success_response_no_data()

    token = link_record.orcid_auth.access_token

    # TODO: handle error? or propagate?
    orcid_oauth(token).revoke_token()

    model = StorageModel()

    # TODO: handle error? or propagate?
    model.remove_user_record(username)

    return success_response_no_data()


@router.get(
    "",
    response_model=LinkRecordPublic,
    tags=["link"],
    responses={
        **AUTH_RESPONSES,
        404: {"description": "Link not available for this user"},
        # TODO: the model for error results should be typed more precisely - i.e. for each type of error response.
        422: {"description": "Either input or output data does not comply with the API schema", "model": ErrorResponse}
    }
)
async def link(
        authorization: str | None = AUTHORIZATION_HEADER
) -> LinkRecordPublic:
    """
    Return the link for the user associated with the KBase auth token passed in the "Authorization" header
    """
    authorization = ensure_authorization(authorization)
    username = get_username(authorization)
    link_record = get_link_record(username)

    if link_record is None:
        return error_response("notFound", "Not Linked", "No link record was found for this user", status_code=404)

    return LinkRecordPublic(
        created_at=link_record.created_at,
        expires_at=link_record.expires_at,
        orcid_auth=ORCIDAuthPublic(
            name=link_record.orcid_auth.name,
            scope=link_record.orcid_auth.scope,
            expires_in=link_record.orcid_auth.expires_in,
            orcid=link_record.orcid_auth.orcid
        )
    )


@router.get(
    "/is_linked",
    response_model=bool,
    tags=["link"],
    responses={
        **AUTH_RESPONSES
    }
)
async def is_linked(
        authorization: str | None = AUTHORIZATION_HEADER
) -> bool:
    """
    Determine if the user associated with the KBase auth token in the "Authorization" header has a 
    link to an ORCID account.
    """
    authorization = ensure_authorization(authorization)

    username = get_username(authorization)

    link_record = get_link_record(username, ignore_errors=True)

    return link_record is not None
