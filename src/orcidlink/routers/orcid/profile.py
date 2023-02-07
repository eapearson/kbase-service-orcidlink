from typing import List

from fastapi import APIRouter
from orcidlink import model
from orcidlink.lib.errors import NotFoundError
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    STD_RESPONSES,
)
from orcidlink.model import ORCIDProfile
from orcidlink.service_clients import orcid_api
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
# Utilities
#


def transform_affilations(
    affiliation_group: orcid_api.ORCIDAffiliationGroup
    | List[orcid_api.ORCIDAffiliationGroup],
) -> List[model.ORCIDAffiliation]:
    def coerce_to_list(
        from_orcid: orcid_api.ORCIDAffiliationGroup
        | List[orcid_api.ORCIDAffiliationGroup],
    ) -> List[orcid_api.ORCIDAffiliationGroup]:
        if isinstance(from_orcid, orcid_api.ORCIDAffiliationGroup):
            return [from_orcid]
        elif isinstance(from_orcid, list):
            return from_orcid

    aff_group = coerce_to_list(affiliation_group)

    affiliations = []
    for affiliation in aff_group:
        #
        # For some reason there is a list of summaries here, but I don't
        # see such a structure in the XML, so just take the first element.
        #
        employment_summary = affiliation.summaries[0].employment_summary
        name = employment_summary.organization.name
        role = employment_summary.role_title
        start_year = employment_summary.start_date.year.value
        if employment_summary.end_date is not None:
            end_year = employment_summary.end_date.year.value
        else:
            end_year = None

        affiliations.append(
            model.ORCIDAffiliation(
                name=name, role=role, startYear=start_year, endYear=end_year
            )
        )
    return affiliations


def get_profile_to_ORCIDProfile(
    orcid_id: str, profile_raw: orcid_api.ORCIDProfile
) -> ORCIDProfile:
    email_addresses = []
    for email in profile_raw.person.emails.email:
        email_addresses.append(email.email)

    # probably should translate into something much simpler...
    # also maybe have a method per major chunk of profile?

    first_name = profile_raw.person.name.given_names.value
    last_name = profile_raw.person.name.family_name.value
    bio = profile_raw.person.biography.content

    # Organizations / Employment!

    affiliation_group = profile_raw.activities_summary.employments.affiliation_group
    affiliations = transform_affilations(affiliation_group)

    #
    # Publications
    works = []

    activity_works = profile_raw.activities_summary.works.group
    for work in activity_works:
        work_summary = work.work_summary[0]
        # get_raw_prop(work, ["work-summary", 0], None)
        works.append(to_service.raw_work_summary_to_work(work_summary))

    return ORCIDProfile(
        orcidId=orcid_id,
        firstName=first_name,
        lastName=last_name,
        bio=bio,
        affiliations=affiliations,
        works=works,
        emailAddresses=email_addresses,
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

    Returns a 404 Not Found if the user is not linked
    """
    _, token_info = ensure_authorization(authorization)
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
    profile_json = orcid_api.orcid_api(access_token).get_profile(orcid_id)

    return get_profile_to_ORCIDProfile(orcid_id, profile_json)
