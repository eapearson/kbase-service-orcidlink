import json
from typing import Union

import requests
import yaml
from fastapi import FastAPI, HTTPException, Header, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from lib.auth import get_username
from lib.config import get_config, get_service_path
from lib.exceptions import KBaseAuthException
from lib.responses import error_response
from lib.storage_model import StorageModel
from lib.transform import orcid_api_url, raw_work_to_work
from lib.utils import get_int_prop, get_kbase_config, get_prop
from model_types import KBaseConfig, LinkRecord, ORCIDProfile, SimpleSuccess
from routers import doiorg, linking_sessions, works
from routers.doi_forms import root

app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

app.include_router(works.router)
app.include_router(linking_sessions.router)
app.include_router(doiorg.router)
app.include_router(root.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            'code': 'unprocessable_entity',
            'message': 'This request does not comply with the schema for this endpoint',
            "data": {
                "detail": exc.errors(),
                "body": exc.body
            }
        }),
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder({
            'code': 'internal_server_error',
            'message': 'An internal server error was detected'
        })
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder({
                'code': 'not_found',
                'message': 'The requested resource was not found',
                'data': {
                    'path': request.url.path
                }
            })
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({
            'code': 'fastapi_exception',

        })
    )


@app.exception_handler(KBaseAuthException)
async def kbase_auth_exception_handler(request: Request, exc: KBaseAuthException):
    return JSONResponse(
        # TODO: this should reflect the nature of the auth error,
        # probably either 401, 403, or 500.
        status_code=401,
        content=jsonable_encoder({
            'code': 'autherror',
            'message': exc.message,
            'data': {
                'upstream_error': exc.upstream_error,
                'exception_string': exc.exception_string
            }
        })
    )


################################
# API
################################


class StatusResponse(BaseModel):
    status: str = Field(...)
    kbase_config: KBaseConfig = Field(...)


@app.get("/status", response_model=StatusResponse)
async def get_status():
    with open(get_kbase_config(), 'r') as kbase_config_file:
        kbase_config = yaml.load(kbase_config_file, yaml.SafeLoader)
        return {"status": "ok", "kbase_config": kbase_config}


#
# Link management
#


@app.delete("/link", response_model=SimpleSuccess)
async def delete_link(authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401, 'Authorization required')

    username = get_username(authorization)

    model = StorageModel()

    user_record = model.get_user_record(username)
    # TODO error if user_record not found
    token = user_record["orcid_auth"]["access_token"]

    url = f"{get_config(['orcid', 'tokenRevokeURL'])}"
    header = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": get_config(["env", "CLIENT_ID"]),
        "client_secret": get_config(["env", "CLIENT_SECRET"]),
        "token": token,
    }
    response = requests.post(url, headers=header, data=data)

    model.remove_user_record(username)
    return {"ok": True}


@app.get("/link", response_model=Union[LinkRecord, None])
async def link(authorization: str | None = Header(default=None)):
    username = get_username(authorization)
    try:
        model = StorageModel()
        user_record = model.get_user_record(username)
    except Exception as ex:
        raise HTTPException(400, {
            "code": "abc",
            "message": "Error fetching user record",
            "detail": str(ex)
        })

    if user_record is None:
        return None
    else:
        return user_record


@app.get("/profile", response_model=ORCIDProfile)
async def get_profile(authorization: str | None = Header(default=None)):
    username = get_username(authorization)

    #
    # Fetch the user's ORCID record from KBase.
    #
    model = StorageModel()
    user_record = model.get_user_record(username)
    if user_record is None:
        return error_response("notfound", "User record not found", status_code=404)

    # Extract our simplified, flattened form of the
    # profile.
    token = user_record["orcid_auth"]["access_token"]
    orcid_id = user_record["orcid_auth"]["orcid"]

    #
    # Get the user's profile from ORCID
    #
    header = {
        "Accept": "application/vnd.orcid+json",
        "Authorization": f"Bearer {token}",
    }
    url = orcid_api_url(f"{orcid_id}/record")
    response = requests.get(url, headers=header)

    profile_json = json.loads(response.text)

    url = orcid_api_url(f"{orcid_id}/email")
    response = requests.get(url, headers=header)
    email_json = json.loads(response.text)
    emails = get_prop(email_json, ['email'])
    email_addresses = []
    for email in emails:
        email_addresses.append(get_prop(email, ['email']))

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
    activity_works = get_prop(profile_json, ["activities-summary", "works", "group"], [])
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
        "emailAddresses": email_addresses
    }

    return profile


class GetIsLinkedResult(BaseModel):
    result: bool = Field(...)


@app.get("/is_linked", response_model=GetIsLinkedResult)
async def is_linked(authorization: str | None = Header(default=None)):
    username = get_username(authorization)
    model = StorageModel()
    user_record = model.get_user_record(username)
    return {"result": user_record is not None}


# Docs

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    # root_path = req.scope.get("root_path", "").rstrip("/")

    root_path = get_service_path()
    print('DOCS', root_path, app.openapi_url)
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )
