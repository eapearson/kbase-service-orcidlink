import json
from typing import List

import requests
from fastapi import APIRouter, HTTPException, Header
from lib.auth import get_username
from lib.storage_model import StorageModel
from lib.transform import orcid_api_url, parse_date, raw_work_to_work
from lib.utils import get_prop
from pydantic import BaseModel, Field

from src.model_types import ExternalId, ORCIDWork, SimpleSuccess

router = APIRouter(
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
@router.get("/works/{put_code}", response_model=ORCIDWork)
async def get_works_entity(put_code: str, authorization: str | None = Header(default=None)):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    # TODO error if user_record not found
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]
    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api_url(f"{orcid_id}/work/{put_code}")
    response = requests.get(url, headers=header)
    return raw_work_to_work(json.loads(response.text))


##
# Get all works from the user linked to the KBase authentication token
#

class GetWorksResult(BaseModel):
    result: List[ORCIDWork]


@router.get("/works", response_model=GetWorksResult)
async def get_works(authorization: str | None = Header(default=None)):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    # TODO error if user_record not found
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]
    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    # header = {"Accept": "application/vnd.orcid+xml", "Authorization": f"Bearer {token}"}
    url = orcid_api_url(f"{orcid_id}/works")
    response = requests.get(url, headers=header)
    # works_json = xmltodict.parse(response.text)
    # profile_xml = ET.fromstring(response.text)
    # profile_json = xmltodict.parse(response.text)
    # probably should translate into something much simpler...
    # also maybe have a method per major chunk of profile?

    return {"result": json.loads(response.text)}


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


@router.put("/works", response_model=ORCIDWork)
async def save_work(
        work_update: WorkUpdate, authorization: str | None = Header(default=None)
):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    # TODO error if user_record not found
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]
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

    url = orcid_api_url(f"{orcid_id}/work/{put_code}")
    header = {
        "Accept": "application/vnd.orcid+json",
        "Content-Type": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.put(url, headers=header, data=json.dumps(work_record))

    return raw_work_to_work(json.loads(response.text))


def get_orcid_auth(kbase_token):
    username = get_username(kbase_token)
    model = StorageModel()
    user_record = model.get_user_record(username)
    return user_record


@router.delete("/works/{put_code}", response_model=SimpleSuccess)
async def delete_work(put_code: str, authorization: str | None = Header(default=None)):
    user_record = get_orcid_auth(authorization)
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]
    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api_url(f"{orcid_id}/work/{put_code}")

    response = requests.delete(url, headers=header)
    return {"ok": True}


@router.post("/works", response_model=ORCIDWork)
async def create_work(
        new_work: NewWork, authorization: str | None = Header(default=None)
):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    # TODO error if user_record not found
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]

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
