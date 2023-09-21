from fastapi import APIRouter
from starlette.responses import JSONResponse

from orcidlink import process
from orcidlink.lib import exceptions
from orcidlink.lib.auth import ensure_authorization
from orcidlink.lib.responses import AUTH_RESPONSES, AUTHORIZATION_HEADER, STD_RESPONSES
from orcidlink.lib.service_clients import orcid_api
from orcidlink.model import ORCIDProfile
from orcidlink.translators import to_service

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

    user_link_record = await process.link_record_for_user(username)
    if user_link_record is None:
        raise exceptions.NotFoundError(message="ORCID Profile Not Found")

    # Extract our simplified, flattened form of the profile.
    access_token = user_link_record.orcid_auth.access_token
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #

    # TODO: what if the profile is not found?
    profile_json = await orcid_api.orcid_api(access_token).get_profile(orcid_id)

    return to_service.orcid_profile(profile_json)
