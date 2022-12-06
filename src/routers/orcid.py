import json
from typing import Union

import requests
from fastapi import APIRouter, Header, HTTPException

from lib.auth import get_username
from lib.config import get_config
from lib.ORCIDClient import orcid_api
from lib.responses import auth_required_error_response, error_response
from lib.storage_model import StorageModel
from lib.transform import orcid_api_url, raw_work_to_work
from lib.utils import get_int_prop, get_prop
from model_types import LinkRecord, ORCIDProfile, SimpleSuccess

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


@router.get(
    "/profile", 
    response_model=ORCIDProfile, 
    tags=["orcid"],
    responses={
        404: {"description": "User not linked or ORCID profile not available."}
    }
)
async def get_profile(authorization: str | None = Header(default=None)):
    """
    Get the ORCID profile for the user associated with the current auth token.

    Returns a 404 Not Found if the user is not linked
    """
    username = get_username(authorization)

    #
    # Fetch the user's ORCID Link record from KBase.
    #
    model = StorageModel()
    user_link_record = model.get_user_record(username)
    if user_link_record is None:
        return error_response("notfound", "User link record not found", status_code=404)

    # Extract our simplified, flattened form of the profile.
    token = user_link_record.orcid_auth.access_token 
    orcid_id = user_link_record.orcid_auth.orcid

    #
    # Get the user's profile from ORCID
    #

    # TODO: this should be wrapped in an ORCID, or may the ORCID Link client
    # orcid_ = ORCIDApi(get_config(['orcid', 'apiBaseURL']), token)

  
    # TODO: what if the profile is not found?
    profile_json = orcid_api(token).get_profile(orcid_id)

    email_json = orcid_api(token).get_email(orcid_id)
    

    emails = get_prop(email_json, ["email"])
    email_addresses = []
    for email in emails:
        email_addresses.append(get_prop(email, ["email"]))

    # probably should translate into something much simpler...
    # also maybe have a method per major chunk of profile?

    first_name = get_prop(
        profile_json,
        ["person", "name", "given-names", "value"],
    )
    last_name = get_prop(
        profile_json,
        ["person", "name", "family-name", "value"],
    )
    bio = get_prop(
        profile_json,
        [
            "person",
            "biography",
            "content",
        ],
    )

    # Organizations / Employment!

    affiliation_group = get_prop(
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
        employment_summary = get_prop(
            affiliation, ["summaries", 0, "employment-summary"]
        )

        name = get_prop(employment_summary, ["organization", "name"])
        role = get_prop(employment_summary, ["role-title"])
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
    activity_works = get_prop(
        profile_json, ["activities-summary", "works", "group"], []
    )
    for work in activity_works:
        work_summary = get_prop(work, ["work-summary", 0], None)
        works.append(raw_work_to_work(work_summary))

    profile = {
        "orcidId": orcid_id,
        "firstName": first_name,
        "lastName": last_name,
        "bio": bio,
        "affiliations": affiliations,
        "works": works,
        "emailAddresses": email_addresses,
    }

    return ORCIDProfile.parse_obj(profile)
