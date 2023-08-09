from fastapi import APIRouter
from orcidlink.lib.errors import NotFoundError
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    STD_RESPONSES,
)
from orcidlink.model import ORCIDProfile
from orcidlink.lib.service_clients import orcid_api
from orcidlink.service_clients.auth import ensure_authorization
from orcidlink.storage.storage_model import storage_model
from orcidlink.translators import to_service
from starlette.responses import JSONResponse

################################
# API
################################


router = APIRouter(
    prefix="/orcid/profile", responses={404: {"description": "Not found"}}
)


#
# API
#


@router.get(
    "",
    response_model=ORCIDProfile,
    tags=["orcid"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "User not linked or ORCID profile not available."},
        200: {"description": ""},
    },
)
async def get_profile(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> ORCIDProfile | JSONResponse:
    """
    Get the ORCID profile for the user associated with the current auth token.

    Since ORCID Link is not a general purpose ORCID api, we may not fully
    represent the profile as ORCID does, but modify it for purpose.
    E.g. ORCID work records have a lot of optional fields which we
    actually require. This is reflected in the typing. So we can't really
    provide all work records in the profile, just those created by
    KBase.

    Returns a 404 Not Found if the user is not linked
    """
    _, token_info = await ensure_authorization(authorization)
    username = token_info.user

    #
    # Fetch the user's ORCID Link record from KBase.
    #
    user_link_record = storage_model().get_link_record(username)
    if user_link_record is None:
        raise NotFoundError(message="User link record not found")
        # return error_response(
        #     "notfound", "Not Found", "User link record not found", status_code=404
        # )

    # Extract our simplified, flattened form of the profile.
    access_token = user_link_record.orcid_auth.access_token
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #

    # TODO: what if the profile is not found?
    profile_json = await orcid_api.orcid_api(access_token).get_profile(orcid_id)

    return to_service.orcid_profile(profile_json)
