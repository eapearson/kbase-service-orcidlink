from fastapi import APIRouter, Header
from lib.auth import get_username
from lib.authclient import KBaseAuthException, KBaseAuthInvalidToken, KBaseAuthMissingToken
from lib.db import FileStorage
from lib.responses import error_response, exception_response

router = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
)


@router.get("/requests")
async def get_doi_requests(
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

    admins = ['eapearson']

    if username not in admins:
        return error_response('not_admin', 'Admin features restricted to service administrators', status_code=403)

    db = FileStorage()
    applications = db.list('doi-requests')

    def sorter(app):
        return app['response']['at']

    applications.sort(key=sorter, reverse=True)

    return applications


@router.get("/forms")
async def get_doi_applications(
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

    admins = ['eapearson']

    if username not in admins:
        return error_response('not_admin', 'Admin features restricted to service administrators', status_code=403)

    db = FileStorage()
    applications = db.list('doi-forms')

    def sorter(app):
        return app['updated_at']

    applications.sort(key=sorter, reverse=True)

    return applications
