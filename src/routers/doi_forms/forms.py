import uuid
from typing import List

from fastapi import APIRouter, Header
from lib.auth import get_username
from lib.authclient import KBaseAuthException, KBaseAuthInvalidToken, KBaseAuthMissingToken
from lib.db import FileStorage
from lib.json_file import get_json_file
from lib.responses import error_response, exception_response
from lib.utils import current_time_millis
from pydantic import BaseModel, Field
from routers.doi_forms.forms_types import DOIApplicationUpdate, DOIFormRecord, InitialDOIApplication, OSTISubmission

router = APIRouter(
    prefix="/forms",
    responses={404: {"description": "Not found"}},
)


class ReviewAndSubmitSectionParams(BaseModel):
    submission: OSTISubmission


class ReviewAndSubmitSectionResult(BaseModel):
    requestId: str = Field(...)


#
# ENDPOINTS
#

@router.post("", response_model=DOIFormRecord)
async def create_doi_form(
        doi_form: InitialDOIApplication, authorization: str | None = Header(default=None)
):
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

    db = FileStorage()
    form_id = str(uuid.uuid4())
    application = doi_form.dict(exclude_unset=True)
    application['form_id'] = form_id
    application['owner'] = username
    application['created_at'] = current_time_millis()
    application['updated_at'] = current_time_millis()
    db.create('doi-forms', form_id, application)
    return application


@router.put("", response_model=DOIFormRecord)
async def update_doi_form(
        doi_form: DOIApplicationUpdate, authorization: str | None = Header(default=None)
):
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

    db = FileStorage()
    form = db.get('doi-forms', doi_form.form_id)

    if form['owner'] != username:
        return error_response("auth", "You do not own this form", status_cod=403)

    form['status'] = doi_form.status
    form['sections'] = doi_form.sections.dict(exclude_unset=True)
    form['updated_at'] = current_time_millis()
    db.update('doi-forms', doi_form.form_id, form)
    return form


@router.get("/{form_id}", response_model=DOIFormRecord)
async def get_doi_form(
        form_id: str, authorization: str | None = Header(default=None)
):
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

    db = FileStorage()
    form = db.get('doi-forms', form_id)

    if form['owner'] != username:
        return error_response("auth", "You do not own this form", status_cod=403)

    return form


@router.delete("/{form_id}")
async def delete_doi_application(
        form_id: str, authorization: str | None = Header(default=None)
):
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

    db = FileStorage()
    application = db.get('doi-forms', form_id)

    if application['owner'] != username:
        return error_response("auth", "You do not own this application", {})

    db.delete('doi-forms', form_id)


@router.get("", response_model=List[DOIFormRecord])
async def get_doi_forms(
        authorization: str = Header(...)
):
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

    db = FileStorage()
    applications = db.list('doi-forms')
    user_applications = [application for application in applications if application['owner'] == username]

    def sorter(app):
        return app['updated_at']

    user_applications.sort(key=sorter, reverse=True)

    return user_applications


@router.get("/osti_contributor_types")
async def get_osti_contributor_types():
    try:
        result = get_json_file('osti-contributor-types')
        return {
            "osti_contributor_types": result
        }
    except Exception as ex:
        return exception_response(ex)
