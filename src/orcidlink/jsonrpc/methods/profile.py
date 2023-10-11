from orcidlink import process
from orcidlink.jsonrpc.errors import (
    NotFoundError,
    ORCIDUnauthorizedClient,
    UpstreamError,
)
from orcidlink.lib.service_clients import orcid_api
from orcidlink.model import ORCIDProfile
from orcidlink.translators import to_service


async def get_profile(username: str) -> ORCIDProfile:
    user_link_record = await process.link_record_for_user(username)
    if user_link_record is None:
        raise NotFoundError("ORCID Profile Not Found")

    # Extract our simplified, flattened form of the profile.
    access_token = user_link_record.orcid_auth.access_token
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #
    try:
        profile_json = await orcid_api.orcid_api(access_token).get_profile(orcid_id)
    except orcid_api.ORCIDAPIAccountNotFoundError as err:
        raise NotFoundError(err.message)
    except orcid_api.ORCIDAPIClientInvalidAccessTokenError as err:
        raise ORCIDUnauthorizedClient(err.message)
    except orcid_api.ORCIDAPIClientOtherError as err:
        raise UpstreamError(err.message)

    profile = to_service.orcid_profile(profile_json)

    return profile
