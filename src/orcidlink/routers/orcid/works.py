import json
from typing import List, Optional

import httpx
from fastapi import APIRouter, Body, HTTPException, Path
from orcidlink import model
from orcidlink.lib.config import config
from orcidlink.lib.errors import ServiceError
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    ErrorResponse,
    STD_RESPONSES,
    error_response,
    success_response_no_data,
)
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.model import UnknownError
from orcidlink.service_clients import orcid_api
from orcidlink.service_clients.auth import ensure_authorization, get_username
from orcidlink.storage.storage_model import storage_model
from orcidlink.translators import to_orcid, to_service
from starlette.responses import JSONResponse, Response

router = APIRouter(prefix="/orcid/works", responses={404: {"description": "Not found"}})


#
# Utils
#


def get_link_record(kbase_token: str) -> Optional[model.LinkRecord]:
    username = get_username(kbase_token)
    model = storage_model()
    return model.get_link_record(username)


def link_record_not_found() -> JSONResponse:
    return error_response(
        "notFound", "Not Found", "ORCID link record not found for user", status_code=404
    )


#
# Works
#


##
# Get a single work from the user linked to the KBase authentication token,
# identified by the put_code.
#
@router.get(
    "/{put_code}",
    response_model=model.ORCIDWork,
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
) -> model.ORCIDWork | JSONResponse:
    """
    Fetch the work record, identified by `put_code`, for the user associated with the KBase auth token provided in the `Authorization` header
    """
    authorization, _ = ensure_authorization(authorization)

    link_record = get_link_record(authorization)

    if link_record is None:
        return link_record_not_found()

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    try:
        raw_work = orcid_api.orcid_api(token).get_work(orcid_id, put_code)
        return to_service.raw_work_to_work(raw_work.bulk[0].work)
    except ServiceError as err:
        return err.get_response()
    except Exception as ex:
        raise ServiceError(
            error=ErrorResponse[ServiceBaseModel](
                code="upstreamError",
                title="Error",
                message="Exception calling ORCID endpoint",
                data=UnknownError(exception=str(ex)),
            ),
            status_code=400,
        )


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
) -> List[model.ORCIDWorkGroup] | JSONResponse:
    """
    Fetch all of the "work" records from a user's ORCID account if their KBase account is linked.
    """
    authorization, _ = ensure_authorization(authorization)

    link_record = get_link_record(authorization)

    if link_record is None:
        return link_record_not_found()

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    orcid_works = orcid_api.orcid_api(token).get_works(orcid_id)
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
                    to_service.raw_work_summary_to_work(work_summary)
                    for work_summary in group.work_summary
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
        200: {"model": model.ORCIDWork},
    },
)
async def save_work(
    work_update: model.WorkUpdate,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> model.ORCIDWork | JSONResponse:
    """
    Update a work record; the `work_update` contains the `put code`.
    """
    authorization, _ = ensure_authorization(authorization)

    link_record = get_link_record(authorization)

    if link_record is None:
        return link_record_not_found()

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    put_code = work_update.putCode

    #
    # First, get the work record.
    #
    get_work_result = orcid_api.orcid_api(token).get_work(orcid_id, put_code)
    work_record = get_work_result.bulk[0].work

    work_record_updated = to_orcid.translate_work_update(work_update, work_record)

    # TODO: check this
    raw_work_record = orcid_api.orcid_api(token).save_work(
        orcid_id, put_code, work_record_updated
    )

    return to_service.raw_work_to_work(raw_work_record)


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
) -> JSONResponse | Response:
    authorization, _ = ensure_authorization(authorization)

    link_record = get_link_record(authorization)

    if link_record is None:
        return link_record_not_found()

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api.orcid_api_url(f"{orcid_id}/work/{put_code}")

    response = httpx.delete(url, headers=header)

    if response.status_code == 204:
        return success_response_no_data()

    return error_response(
        "orcid-api-error",
        "ORCID API Error",
        "The ORCID API reported an error fo this request, see 'data' for cause",
        data=response.json(),
    )


@router.post(
    "",
    tags=["works"],
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {
            "description": "Work record successfully created",
            "model": model.ORCIDWork,
        },
    },
)
async def create_work(
    new_work: model.NewWork = Body(
        description="The new work record to be added to the ORCID profile."
    ),
    authorization: str | None = AUTHORIZATION_HEADER,
) -> JSONResponse | model.ORCIDWork:
    authorization, _ = ensure_authorization(authorization)

    link_record = get_link_record(authorization)

    if link_record is None:
        return link_record_not_found()

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    #
    # Create initial work record
    #

    external_ids: List[orcid_api.ORCIDExternalId] = []
    if new_work.externalIds is not None:
        for index, externalId in enumerate(new_work.externalIds):
            external_ids.append(
                orcid_api.ORCIDExternalId(
                    external_id_type=externalId.type,
                    external_id_value=externalId.value,
                    external_id_url=orcid_api.StringValue(value=externalId.url),
                    external_id_relationship=externalId.relationship,
                )
            )
        # NOTE: yes, it is odd that "external-ids" takes a single property
        # "external-id" which itself is the collection of external ids!
        # work_record["external-ids"] = {"external-id": external_ids}

    work_record = orcid_api.NewWork(
        type=new_work.workType,
        title=orcid_api.ORCIDTitle(title=orcid_api.StringValue(value=new_work.title)),
        journal_title=orcid_api.StringValue(value=new_work.journal),
        url=orcid_api.StringValue(value=new_work.url),
        external_ids=orcid_api.ExternalIds(external_id=external_ids),
        publication_date=to_orcid.parse_date(new_work.date),
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
        bulk=[orcid_api.NewWorkWrapper(work=work_record)]
    )

    # TODO: propagate everywhere. Or, perhaps better,
    # wrap this common use case into a function or class.
    timeout = config().module.serviceRequestTimeout / 1000
    try:
        response = httpx.post(
            url,
            timeout=timeout,
            headers=header,
            content=json.dumps(content.dict(by_alias=True)),
        )
    except httpx.HTTPError as ex:
        raise HTTPException(
            400,
            {
                "code": "foo",
                "message": "An error was encountered saving the work record",
                "description": str(ex),
            },
        )
    if response.status_code == 200:
        work_record2 = orcid_api.GetWorkResult.parse_obj(json.loads(response.text))
        # TODO: handle errors here; they are not always
        new_work_record = to_service.raw_work_to_work(work_record2.bulk[0].work)
        return new_work_record
    else:
        if response.status_code == 500:
            raise HTTPException(
                500,
                {
                    "code": "internalserver",
                    "message": "Internal Server Error",
                    "data": {"responseText": response.text},
                },
            )
        error = json.loads(response.text)
        raise HTTPException(
            400,
            {
                "code": "fastapi",
                # TODO: error should be typed
                "message": error["user-message"],
                "data": error,
            },
        )
