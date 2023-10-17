"""
Implements the "get-orcid-profile" JSON-RPC method and associated types, if any
"""

from orcidlink import process
from orcidlink.jsonrpc.errors import NotAuthorizedError, NotFoundError
from orcidlink.lib.service_clients import orcid_api
from orcidlink.model import ORCIDProfile
from orcidlink.translators import to_service


async def get_profile(username: str, auth_username: str) -> ORCIDProfile:
    """
    Fetches the ORCID profile for the given KBase user.

    This method works only for the owner of the link. That is, it enforces the
    rule that the requested orcid profile must be for the same user as
    authorized.

    Returns an ORCIDProfile, which is a simplified version of the user's ORCID profile
    record.

    May raise the following errors:
    - NotAuthorizedError - if the requested user and authorized user are not the same
    - NotFoundError - if the requested user does not have an ORCID Link
    - NotFoundError - if the ORCID Link's orcid id does not match an account at ORCID
    - ORCIDUnauthorizedClient - if the ORCID Link's access token is invalid, and a
        token refresh couldn't fix it.
    - UpstreamError - if the ORCID API returned any other error
    """
    if username != auth_username:
        raise NotAuthorizedError("Only the link owner may request their profile")

    user_link_record = await process.link_record_for_user(username)

    if user_link_record is None:
        raise NotFoundError("KBase ORCID Link not found for this user")

    # Extract our simplified, flattened form of the profile.
    access_token = user_link_record.orcid_auth.access_token
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #
    print("ABOUT TO CALL", access_token, orcid_id)
    profile_json = await orcid_api.orcid_api(access_token).get_profile(orcid_id)
    # try:
    #     profile_json = await orcid_api.orcid_api(access_token).get_profile(orcid_id)
    # except orcid_api.ORCIDAPINotFoundError as err:
    #     raise NotFoundError(err.message) from err
    # except orcid_api.ORCIDAPIClientInvalidAccessTokenError as err:
    #     raise ORCIDInsufficientAuthorizationError(err.message) from err
    # except orcid_api.ORCIDAPIClientOtherError as err:
    #     raise UpstreamError(err.message) from err

    return to_service.orcid_profile(profile_json)
