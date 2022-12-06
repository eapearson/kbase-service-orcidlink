import json
from typing import List

import requests
from fastapi import APIRouter, Header, HTTPException, Path
from pydantic import BaseModel, Field

from lib.auth import get_username
from lib.ORCIDClient import orcid_api
from lib.responses import (ErrorException, ErrorResponse, ensure_authorization,
                           error_response, make_error_exception, to_json)
from lib.storage_model import StorageModel
from lib.transform import orcid_api_url, parse_date, raw_work_to_work
from lib.utils import get_prop
from src.model_types import ExternalId, LinkRecord, ORCIDWork, SimpleSuccess

router = APIRouter(
    prefix="/works",
    responses={404: {"description": "Not found"}}
)


class WorkUpdate(BaseModel):
    putCode: int = Field(...)
    title: str = Field(None)
    journal: str = Field(None)
    date: str = Field(None)
    workType: str = Field(None)
    url: str = Field(None)
    externalIds: List[ExternalId] = Field(None)


class NewWork(BaseModel):
    title: str = Field(...)
    journal: str = Field(...)
    date: str = Field(...)
    workType: str = Field(...)
    url: str = Field(...)
    externalIds: List[ExternalId] = Field(...)


#
# Works
#

##
# Get a single work from the user linked to the KBase authentication token,
# identified by the put_code.
#
@router.get(
    "/{put_code}", 
    response_model=ORCIDWork, 
    tags=["works"],
    responses={
        401: {"description": "Token missing or invalid"},
        404: {"description": "Link not available for this user"},
        # TODO: the model for error results should be typed more precisely - i.e. for each type of error response.
        422: {"description": "Either input or output data does not comply with the API schema", "model": ErrorResponse}
    }
)
async def get_works_entity(
    put_code: str = Path(description="The ORCID `put code` for the work record to fetch"), 
    authorization: str | None = Header(default=None, description="Kbase auth token")):
    """
    Fetch the work record, identified by `put_code`, for the user associated with the KBase auth token provided in the `Authorization` header
    """

    authorization = ensure_authorization(authorization)
    
    username = get_username(authorization)

    model = StorageModel()
    user_record = model.get_user_record(username)
    if user_record is None:
        return error_response("notFound", "User link record not found", status_code=404)

    token = user_record.orcid_auth.access_token
    orcid_id = user_record.orcid_auth.orcid

    # TODO: wrap this into an api class!

    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearerx {token}",
    }
    url = orcid_api_url(f"{orcid_id}/work/{put_code}")
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        data = {
            "originalStatusCode": response.status_code,
        }
        try:
            json_response = json.loads(response.text)
            # Remove potentially revealing information
            # TODO: send note to the ORCID folks asking them to omit the 
            # token from the error response.
            if response.status_code == 401 or response.status_code == 403:
                del json_response['error_description']
            data['originalResponseJSON'] = json_response
        except Exception:
            data['originalResponseText'] = response.text
        raise ErrorException(
            error=ErrorResponse(
                code="upstreamError",
                title="Error",
                message="Error fetching Work record",
                data=data
            ),
            status_code=400
        )

    return raw_work_to_work(to_json(response.text))


##
# Get all works from the user linked to the KBase authentication token
#

class GetWorksResult(BaseModel):
    # TODO: more fields, or is this enough?
    result: List[ORCIDWork]

def get_link_record(username: str, ignore_errors=False) -> LinkRecord:
    model = StorageModel()
    user_record = model.get_user_record(username)
    if user_record is None:
        if ignore_errors:
            return None
        raise make_error_exception("notFound", "Not Found", "User link record not found", status_code=404)
    
    return user_record


def get_pubic_link_record(username: str) -> LinkRecord:
    model = StorageModel()
    user_record = model.get_user_record_public(username)
    if user_record is None:
        raise make_error_exception("notFound", "Not Found", "User link record not found", status_code=404)
    
    return user_record

@router.get(
    "", 
    response_model=GetWorksResult, 
    tags=["works"],
    responses={
        401: {"description": "Token missing or invalid"},
        404: {"description": "Link not available for this user"},
        # TODO: the model for error results should be typed more precisely - i.e. for each type of error response.
        422: {"description": "Either input or output data does not comply with the API schema", "model": ErrorResponse}
    }
)
async def get_works(
    authorization: str | None = Header(default=None, description="Kbase auth token")
):
    """
    Fetch all of the "work" records from a user's ORCID account if their KBase account is linked.
    """
    authorization = ensure_authorization(authorization)
    
    username = get_username(authorization)
    
    link_record = get_link_record(username)

    token = link_record.orcid_auth.access_token
    orcid_id = link_record.orcid_auth.orcid

    full_result = orcid_api(token).get_works(orcid_id)
    result = []
    for group in full_result['group']:
        result.append(raw_work_to_work(group['work-summary'][0]))

    return {"result": result}


# @router.get("/get_work_raw/{put_code}")
# async def get_work_raw(put_code: str, authorization: str | None = Header(default=None)):
#     username = get_username(authorization)
#     model = StorageModel()
#     user_record = model.get_user_record(username)
#     # TODO error if user_record not found
#     token = user_record["orcid_auth"]["access_token"]
#     orcid_id = user_record["orcid_auth"]["orcid"]
#     header = {
#         "Accept": "application/vnd.orcid+json",
#         "Authorization": f"Bearer {token}",
#     }
#     url = orcid_api_url(f"{orcid_id}/work/{put_code}")
#     response = requests.get(url, headers=header)
#     return {"result": json.loads(response.text)}


@router.put(
    "", 
    response_model=ORCIDWork, 
    tags=["works"],
    responses={
        401: {"description": "Token missing or invalid"},
        404: {"description": "Link not available for this user"},
        # TODO: the model for error results should be typed more precisely - i.e. for each type of error response.
        422: {"description": "Either input or output data does not comply with the API schema", "model": ErrorResponse}
    })
async def save_work(
        work_update: WorkUpdate, 
        authorization: str | None = Header(default=None, description="Kbase auth token")
):
    """
    Update a work record; the `work_update` contains the `put code`.
    """
    authorization = ensure_authorization(authorization)

    username = get_username(authorization)

    model = StorageModel()
    user_record = model.get_user_record(username)
    if user_record is None:
        return error_response("notFound", "User link record not found", status_code=404)
    
    token = user_record.orcid_auth.access_token
    orcid_id = user_record.orcid_auth.orcid

    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }

    put_code = work_update.putCode

    #
    # First, get the work record.
    #
    url = orcid_api_url(f"{orcid_id}/work/{put_code}")
    response = requests.get(url, headers=header)
    work_record = json.loads(response.text)

    #
    # Then modify it from the request body
    #
    if work_update.title is not None:
        work_record["title"]["title"]["value"] = work_update.title

    if work_update.workType is not None:
        work_record["type"] = work_update.workType

    if work_update.journal is not None:
        work_record["journal-title"]["value"] = work_update.journal

    if work_update.date is not None:
        work_record["publication-date"] = parse_date(work_update.date)

    if work_update.workType is not None:
        work_record["type"] = work_update.workType

    if work_update.url is not None:
        work_record["url"]["value"] = work_update.url

    if work_update.externalIds is not None:
        for index, externalId in enumerate(work_update.externalIds):
            if index < len(work_record["external-ids"]["external-id"]):
                work_record["external-ids"]["external-id"][index][
                    "external-id-type"
                ] = externalId.type
                work_record["external-ids"]["external-id"][index][
                    "external-id-value"
                ] = externalId.value
                work_record["external-ids"]["external-id"][index]["external-id-url"][
                    "value"
                ] = externalId.url
                work_record["external-ids"]["external-id"][index][
                    "external-id-relationship"
                ] = externalId.relationship
            else:
                work_record["external-ids"]["external-id"].append(
                    {
                        "external-id-type": externalId.type,
                        "external-id-value": externalId.value,
                        "external-id-url": {"value": externalId.url},
                        "external-id-relationship": externalId.relationship,
                    }
                )

    raw_work_record = orcid_api(token).save_work(orcid_id, put_code, work_record)

    # url = orcid_api_url(f"{orcid_id}/work/{put_code}")
    # header = {
    #     "Accept": "application/vnd.orcid+json",
    #     "Content-Type": "application/vnd.orcid+json",
    #     "Authorization": f"Bearer {token}",
    # }
    # response = requests.put(url, headers=header, data=json.dumps(work_record))

    return raw_work_to_work(raw_work_record)


def get_orcid_auth(kbase_token):
    username = get_username(kbase_token)
    model = StorageModel()
    user_record = model.get_user_record(username)
    return user_record


@router.delete("/{put_code}", response_model=SimpleSuccess, tags=["works"])
async def delete_work(
    put_code: str, 
    authorization: str | None = Header(default=None, description="Kbase auth token")
):
    authorization = ensure_authorization(authorization)

    user_record = get_orcid_auth(authorization)

    token = user_record.orcid_auth.access_token
    orcid_id = user_record.orcid_auth.orcid

    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api_url(f"{orcid_id}/work/{put_code}")

    response = requests.delete(url, headers=header)
    return {"ok": True}


@router.post("", response_model=ORCIDWork, tags=["works"])
async def create_work(
        new_work: NewWork, authorization: str | None = Header(default=None)
):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    if user_record is None:
        return error_response("notFound", "User link record not found", status_code=404)

    token = user_record.orcid_auth.access_token
    orcid_id = user_record.orcid_auth.orcid

    #
    # Create initial work record
    #
    work_record = {
        "type": new_work.workType,
        "title": {"title": {"value": new_work.title}},
        "journal-title": {"value": new_work.journal},
        "publication-date": {},
        "url": {"value": new_work.url},
        "external-ids": {"external-id": []}
    }

    if new_work.date is not None:
        work_record["publication-date"] = parse_date(new_work.date)

    if new_work.externalIds is not None:
        for index, externalId in enumerate(new_work.externalIds):
            work_record["external-ids"]["external-id"].append(
                {
                    "external-id-type": externalId.type,
                    "external-id-value": externalId.value,
                    "external-id-url": {"value": externalId.url},
                    "external-id-relationship": externalId.relationship,
                }
            )

    url = orcid_api_url(f"{orcid_id}/works")
    header = {
        "Accept": "application/vnd.orcid+json",
        "Content-Type": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response = requests.post(url, headers=header, data=json.dumps({"bulk": [{"work": work_record}]}))
    except Exception as ex:
        raise HTTPException(400, {
            "code": "foo",
            "message": "An error was encountered saving the work record",
            "description": str(ex)
        })
    if response.status_code == 200:
        json_response = json.loads(response.text)
        new_work_record = raw_work_to_work(get_prop(json_response, ["bulk", 0, "work"]))
        return new_work_record
    else:
        if response.status_code == 500:
            raise HTTPException(500, {
                "code": "internalserver",
                "message": "Internal Server Error",
                "data": {
                    "responseText": response.text
                }
            })
        error = json.loads(response.text)
        raise HTTPException(400, {
            "code": "fastapi",
            "message": get_prop(error, ["user-message"]),
            "data": error
        })
