import uuid

from fastapi import APIRouter, Header
from lib.auth import get_username
from lib.authclient import KBaseAuthException, KBaseAuthInvalidToken, KBaseAuthMissingToken
from lib.db import FileStorage, now
from lib.responses import error_response, exception_response
from pydantic import BaseModel, Field
from routers.demos import OSTIRecord
from routers.doi_forms.forms import OSTISubmission

from lib import ostiapi

router = APIRouter(
    prefix="/doi_requests",
    responses={404: {"description": "Not found"}},
)


class PostDOIRequestParams(BaseModel):
    form_id: str = Field(...)
    submission: OSTISubmission = Field(...)


class GetDOIRequestParams(BaseModel):
    doi: str = Field(None)
    # osti_id: str = Field(None)


class GetDOIRequestResult(BaseModel):
    record: OSTIRecord
    _start: str = Field(...)
    _rows: str = Field(...)
    _numFound: str = Field(...)


class GetDOIRequestResponse(BaseModel):
    result: GetDOIRequestResult


@router.post("")
async def post_doi_request(params: PostDOIRequestParams, authorization: str | None = Header(default=None)):
    try:
        if authorization is None:
            return error_response("auth_token_missing", 'Authentication required', status_code=401)

        try:
            username = get_username(authorization)
        except KBaseAuthMissingToken as ex1:
            return error_response('auth_missing_token', str(ex1))
        except KBaseAuthInvalidToken as ex2:
            return error_response('auth_invalid_token', str(ex2))
        except KBaseAuthException as authex:
            return error_response('auth_error', str(authex))
        except Exception as ex:
            return exception_response(ex)

        ostiapi.testmode()
        response = ostiapi.reserve(params.submission.dict(), username="kbase", password="Sti@2416sub22s")

        # TODO: handle a FAILURE response

        request_id = str(uuid.uuid4())
        fix_field('status', response['record'])
        fix_field('released', response['record'])

        db = FileStorage()
        doi = response['record']['doi']
        record = {
            'username': username,
            'request_id': request_id,
            'form_id': params.form_id,
            'request': {
                'params': params.dict(),
                'at': now()
            },
            'response': {
                'response': response,
                'at': now()
            }
        }
        db.create('doi-requests', request_id, record)

        return {
            'request_id': request_id
        }
    except Exception as ex:
        # TODO: use osti specific exceptions
        return exception_response(ex)


def fix_field(base_name, some_dict):
    some_dict['_' + base_name] = some_dict['@' + base_name]
    del some_dict['@' + base_name]


@router.get("")
async def get_doi_request(doi: str):
    try:
        request_params = {}
        if doi is None:
            raise ValueError('One of "oid" or "osti_id" must be provided')

        db = FileStorage()
        record = db.get('doi-requests', doi)

        return {
            "result": record
        }
    except Exception as ex:
        # TODO: use osti specific exceptions
        return exception_response(ex)


@router.get("/osti")
async def get_osti_doi_request(doi: str):
    try:
        request_params = {}
        if doi is None:
            raise ValueError('One of "oid" or "osti_id" must be provided')
        request_params['doi'] = doi
        ostiapi.testmode()
        result = ostiapi.get(request_params, username="kbase", password="Sti@2416sub22s")
        fix_field('start', result)
        fix_field('rows', result)
        fix_field('numfound', result)

        fix_field('status', result['record'])
        fix_field('released', result['record'])

        return {
            "result": result
        }
    except Exception as ex:
        # TODO: use osti specific exceptions
        return exception_response(ex)
