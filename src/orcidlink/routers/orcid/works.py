import json
from typing import List, Optional

# import httpx
import aiohttp
from fastapi import APIRouter, Body, Path, status
from starlette.responses import Response

from orcidlink import model
from orcidlink.lib import exceptions
from orcidlink.lib.auth import ensure_authorization, get_username
from orcidlink.lib.config import Config2
from orcidlink.lib.responses import AUTH_RESPONSES, AUTHORIZATION_HEADER, STD_RESPONSES
from orcidlink.lib.service_clients import orcid_api
from orcidlink.storage.storage_model import storage_model
from orcidlink.translators import to_orcid, to_service
from orcidlink.translators.to_orcid import (
    transform_contributor_self,
    transform_contributors,
)

router = APIRouter(prefix="/orcid/works", responses={404: {"description": "Not found"}})


#
# Utils
#


async def get_link_record(kbase_token: str) -> Optional[model.LinkRecord]:
    username = await get_username(kbase_token)
    return await storage_model().get_link_record(username)


#
# Works
#


##
# Get a single work from the user linked to the KBase authentication token,
# identified by the put_code.
#
@router.get(
    "/{put_code}",
    response_model=model.Work,
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "Link not available for this user"},
        # TODO: the model for error results should be typed more precisely - i.e. for each type of error response.
    },
)
async def get_work(
    put_code: int = Path(
        description="The ORCID `put code` for the work record to fetch"
    ),
    authorization: str | None = AUTHORIZATION_HEADER,
) -> model.Work:
    """
    Fetch the work record, identified by `put_code`, for the user associated with the KBase auth token provided in the `Authorization` header
    """
    authorization, _ = await ensure_authorization(authorization)

    link_record = await get_link_record(authorization)

    if link_record is None:
        raise exceptions.NotFoundError("ORCID link record not found for user")

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    # try:
    # TODO: move into model
    raw_work = await orcid_api.orcid_api(token).get_work(orcid_id, put_code)
    profile = await orcid_api.orcid_api(token).get_profile(orcid_id)
    return to_service.transform_work(profile, raw_work.bulk[0].work)
    # except errors.ServiceError as err:
    #     # we just catch this so we can release it!
    #     raise err
    # except Exception as ex:
    #     raise errors.UpstreamError(
    #         "Exception calling ORCID API",
    #         data={
    #             "exception": str(ex)
    #         }
    #     )
    # raise ServiceError(
    #     error=ErrorResponse[ServiceBaseModel](
    #         code="upstreamError",
    #         title="Error",
    #         message="Exception calling ORCID endpoint",
    #         data=UnknownError(exception=str(ex)),
    #     ),
    #     status_code=400,
    # )


@router.get(
    "",
    # response_model=Union[List[model.ORCIDWorkGroup], JSONResponse],
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "Link not available for this user"},
        200: {"model": List[model.ORCIDWorkGroup]},
    },
)
async def get_works(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> List[model.ORCIDWorkGroup]:
    """
    Fetch all of the "work" records from a user's ORCID account if their KBase account is linked.
    """
    authorization, _ = await ensure_authorization(authorization)

    link_record = await get_link_record(authorization)

    if link_record is None:
        raise exceptions.NotFoundError("ORCID link record not found for user")

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    orcid_works = await orcid_api.orcid_api(token).get_works(orcid_id)
    result: List[model.ORCIDWorkGroup] = []
    for group in orcid_works.group:
        result.append(
            model.ORCIDWorkGroup(
                updatedAt=group.last_modified_date.value,
                externalIds=[
                    to_service.transform_external_id(external_id)
                    for external_id in group.external_ids.external_id
                ],
                works=[
                    to_service.transform_work_summary(work_summary)
                    # TODO: Need to make the KBase source configurable, as it will be different,
                    # between, say, CI and prod, or at least development and prod.
                    for work_summary in group.work_summary
                    # TODO: replace with source_client_id and compare to the client id
                    # in the config.
                    if work_summary.source.source_name.value == "KBase CI"
                ],
            )
        )

    return result


@router.put(
    "",
    # response_model=model.ORCIDWork,
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "Link not available for this user"},
        200: {"model": model.Work},
    },
)
async def save_work(
    work_update: model.WorkUpdate,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> model.Work:
    """
    Update a work record; the `work_update` contains the `put code`.
    """
    authorization, _ = await ensure_authorization(authorization)

    link_record = await get_link_record(authorization)

    if link_record is None:
        raise exceptions.NotFoundError("ORCID link record not found for user")

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    put_code = work_update.putCode

    work_record_updated = to_orcid.translate_work_update(work_update)

    # TODO: check this
    raw_work_record = await orcid_api.orcid_api(token).save_work(
        orcid_id, put_code, work_record_updated
    )

    profile = await orcid_api.orcid_api(token).get_profile(orcid_id)
    return to_service.transform_work(profile, raw_work_record)


@router.delete(
    "/{put_code}",
    status_code=204,
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        204: {"description": "Work record successfully deleted"},
    },
)
async def delete_work(
    put_code: int,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> Response:
    authorization, _ = await ensure_authorization(authorization)

    link_record = await get_link_record(authorization)

    if link_record is None:
        raise exceptions.NotFoundError("ORCID link record not found for user")

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api.orcid_api_url(f"{orcid_id}/work/{put_code}")

    async with aiohttp.ClientSession() as session:
        async with session.delete(url, headers=header) as response:
            if response.status == 204:
                return Response(status_code=status.HTTP_204_NO_CONTENT)

            # TODO: richer error
            raise exceptions.UpstreamError(
                "The ORCID API reported an error fo this request, see 'data' for cause",
                # data={"upstreamError": await response.json()},
            )

    # return error_response(
    #     "orcid-api-error",
    #     "ORCID API Error",
    #     "The ORCID API reported an error fo this request, see 'data' for cause",
    #     data=response.json(),
    # )


@router.post(
    "",
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": "Work record successfully created",
            "model": model.Work,
        },
    },
)
async def create_work(
    new_work: model.NewWork = Body(
        description="The new work record to be added to the ORCID profile."
    ),
    authorization: str | None = AUTHORIZATION_HEADER,
) -> model.Work:
    authorization, _ = await ensure_authorization(authorization)

    link_record = await get_link_record(authorization)

    if link_record is None:
        raise exceptions.NotFoundError("ORCID link record not found for user")

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    #
    # Create initial work record
    #

    external_ids: List[orcid_api.ExternalId] = [
        orcid_api.ExternalId(
            external_id_type="doi",
            external_id_value=new_work.doi,
            external_id_normalized=None,
            # TODO: doi url should be configurable
            external_id_url=orcid_api.StringValue(
                value=f"https://doi.org/{new_work.doi}"
            ),
            external_id_relationship="self",
        )
    ]

    # external_ids: List[orcid_api.ORCIDExternalId] = []
    if new_work.externalIds is not None:
        for index, externalId in enumerate(new_work.externalIds):
            external_ids.append(
                orcid_api.ExternalId(
                    external_id_type=externalId.type,
                    external_id_value=externalId.value,
                    external_id_url=orcid_api.StringValue(value=externalId.url),
                    external_id_relationship=externalId.relationship,
                )
            )
        # NOTE: yes, it is odd that "external-ids" takes a single property
        # "external-id" which itself is the collection of external ids!
        # work_record["external-ids"] = {"external-id": external_ids}

    citation = orcid_api.Citation(
        citation_type=new_work.citation.type,
        citation_value=new_work.citation.value,
    )

    contributors = []

    self_contributors = transform_contributor_self(new_work.selfContributor)
    contributors.extend(self_contributors)

    contributors.extend(transform_contributors(new_work.otherContributors))

    work_record = orcid_api.NewWork(
        type=new_work.workType,
        title=orcid_api.Title(title=orcid_api.StringValue(value=new_work.title)),
        journal_title=orcid_api.StringValue(value=new_work.journal),
        url=orcid_api.StringValue(value=new_work.url),
        external_ids=orcid_api.ExternalIds(external_id=external_ids),
        publication_date=to_orcid.parse_date(new_work.date),
        short_description=new_work.shortDescription,
        citation=citation,
        contributors=orcid_api.ContributorWrapper(contributor=contributors),
    )

    url = orcid_api.orcid_api_url(f"{orcid_id}/works")
    header = {
        "Accept": "application/vnd.orcid+json",
        "Content-Type": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }

    # Note that we use the "bulk" endpoint because it nicely returns the newly created work record.
    # This both saves a trip and is more explicit than the singular endpoint POST /work, which
    # returns 201 and a location for the new work record, which we would need to parse to
    # extract the put code.
    # TODO: also this endpoint and probably many others return a 200 response with error data.
    content = orcid_api.CreateWorkInput(
        bulk=(orcid_api.NewWorkWrapper(work=work_record),)
    )

    # TODO: propagate everywhere. Or, perhaps better,
    # wrap this common use case into a function or class.
    timeout = Config2().get_request_timeout()
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                url,
                timeout=timeout,
                headers=header,
                data=json.dumps(content.model_dump(by_alias=True)),
            ) as response:
                result = await response.json()
                work_record2 = orcid_api.GetWorkResult.model_validate(result)
                # TODO: handle errors here; they are not always
                profile = await orcid_api.orcid_api(token).get_profile(orcid_id)
                new_work_record = to_service.transform_work(
                    profile, work_record2.bulk[0].work
                )
                return new_work_record
    except aiohttp.ClientError as ex:
        # TODO: richer error here.
        raise exceptions.UpstreamError(
            "An error was encountered saving the work record",
            # data={
            #     "description": str(ex),
            # },
        )

        # raise HTTPException(
        #     400,
        #     {
        #         "code": "foo",
        #         "message": "An error was encountered saving the work record",
        #         "description": str(ex),
        #     },
        # )

    # if response.status_code == 200:
    #     work_record2 = orcid_api.GetWorkResult.model_validate(json.loads(response.text))
    #     # TODO: handle errors here; they are not always
    #     profile = await orcid_api.orcid_api(token).get_profile(orcid_id)
    #     new_work_record = to_service.transform_work(profile, work_record2.bulk[0].work)
    #     return new_work_record
    # elif response.status_code == 500:
    #     raise errors.UpstreamError(
    #         "An error was encountered saving the work record",
    #         data={"upstreamError": {"text": response.text}},
    #     )
    #     # raise HTTPException(
    #     #     500,
    #     #     {
    #     #         "code": "internalserver",
    #     #         "message": "Internal Server Error",
    #     #         "data": {"responseText": response.text},
    #     #     },
    #     # )
    # else:
    #     error = await response.json()
    #     raise errors.UpstreamError(
    #         "The ORCID API reported an error for this request, see 'data' for cause",
    #         data={"upstreamError": error},
    #     )
    #     # raise HTTPException(
    #     #     400,
    #     #     {
    #     #         "code": "fastapi",
    #     #         # TODO: error should be typed
    #     #         "message": error["user-message"],
    #     #         "data": error,
    #     #     },
    #     # )
