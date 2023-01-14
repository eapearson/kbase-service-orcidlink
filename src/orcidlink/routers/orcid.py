from fastapi import APIRouter
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    STD_RESPONSES,
    ensure_authorization,
    error_response,
)
from orcidlink.lib.storage_model import storage_model
from orcidlink.lib.transform import raw_work_to_work
from orcidlink.lib.utils import get_int_prop, get_raw_prop, get_string_prop
from orcidlink.model_types import ORCIDProfile
from orcidlink.service_clients.ORCIDClient import orcid_api
from orcidlink.service_clients.auth import get_username

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

router = APIRouter(prefix="/orcid", responses={404: {"description": "Not found"}})


def orcid_profile_to_normalized(
    orcid_id: str, profile_json, email_json
) -> ORCIDProfile:
    emails = get_raw_prop(email_json, ["email"])
    email_addresses = []
    for email in emails:
        email_addresses.append(get_string_prop(email, ["email"]))

    # probably should translate into something much simpler...
    # also maybe have a method per major chunk of profile?

    first_name = get_string_prop(
        profile_json,
        ["person", "name", "given-names", "value"],
    )
    last_name = get_string_prop(
        profile_json,
        ["person", "name", "family-name", "value"],
    )
    bio = get_string_prop(
        profile_json,
        [
            "person",
            "biography",
            "content",
        ],
    )

    # Organizations / Employment!

    affiliation_group = get_raw_prop(
        profile_json, ["activities-summary", "employments", "affiliation-group"], []
    )

    affiliations = []
    # is an array if more than one, otherwise just a single instance
    if isinstance(affiliation_group, dict):
        affiliation_group = [affiliation_group]

    for affiliation in affiliation_group:
        # employment_summary = get_prop(affiliationaffiliation["employment-summary"]

        #
        # For some reason there is a list of summaries here, but I don't
        # see such a structure in the XML, so just take the first element.
        #
        employment_summary = get_raw_prop(
            affiliation, ["summaries", 0, "employment-summary"]
        )

        name = get_string_prop(employment_summary, ["organization", "name"])
        role = get_string_prop(employment_summary, ["role-title"])
        start_year = get_int_prop(employment_summary, ["start-date", "year", "value"])
        end_year = get_int_prop(employment_summary, ["end-date", "year", "value"])

        affiliations.append(
            {
                "name": name,
                "role": role,
                "startYear": start_year,
                "endYear": end_year,
            }
        )

    #
    # Publications
    works = []
    activity_works = get_raw_prop(
        profile_json, ["activities-summary", "works", "group"], []
    )
    for work in activity_works:
        work_summary = get_raw_prop(work, ["work-summary", 0], None)
        works.append(raw_work_to_work(work_summary))

    return ORCIDProfile(
        orcidId=orcid_id,
        firstName=first_name,
        lastName=last_name,
        bio=bio,
        affiliations=affiliations,
        works=works,
        emailAddresses=email_addresses,
    )


# GET_PROFILE_RESPONSES: ResponseMapping = {
#     404: {"description": "User not linked or ORCID profile not available."},
#     200: {"description": ""}
# }


# GET_PROFILE_RESPONSES | AUTH_RESPONSES | STD_RESPONSES


@router.get(
    "/profile",
    response_model=ORCIDProfile,
    tags=["orcid"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "User not linked or ORCID profile not available."},
        200: {"description": ""},
    }
    # responses={**GET_PROFILE_RESPONSES, **AUTH_RESPONSES, **STD_RESPONSES}
)
async def get_profile(authorization: str | None = AUTHORIZATION_HEADER):
    """
    Get the ORCID profile for the user associated with the current auth token.

    Returns a 404 Not Found if the user is not linked
    """
    authorization = ensure_authorization(authorization)
    username = get_username(authorization)

    #
    # Fetch the user's ORCID Link record from KBase.
    #
    model = storage_model()
    user_link_record = model.get_link_record(username)
    if user_link_record is None:
        return error_response(
            "notfound", "Not Found", "User link record not found", status_code=404
        )

    # Extract our simplified, flattened form of the profile.
    access_token = user_link_record.orcid_auth.access_token
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #

    # TODO: what if the profile is not found?
    profile_json = orcid_api(access_token).get_profile(orcid_id)
    email_json = orcid_api(access_token).get_email(orcid_id)

    return orcid_profile_to_normalized(orcid_id, profile_json, email_json)
