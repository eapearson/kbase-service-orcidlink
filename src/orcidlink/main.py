import json
from urllib.parse import urlencode

import httpx
from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import RedirectResponse
from orcidlink.api_types import InfoResponse, StatusResponse
from orcidlink.lib.config import (config, get_kbase_config, get_service_path, get_service_url)
from orcidlink.lib.responses import (ErrorException, error_response,
                                     exception_error_response, ui_error_response)
from orcidlink.lib.storage_model import storage_model
from orcidlink.lib.utils import epoch_time_millis
from orcidlink.model_types import ORCIDAuth
from orcidlink.routers import link, linking_sessions, orcid, works
from orcidlink.routers.linking_sessions import get_linking_session_record
from orcidlink.service_clients.authclient2 import (KBaseAuthException, KBaseAuthInvalidToken,
                                                   KBaseAuthMissingToken)
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

#
# Set up FastAPI top level app with associated metadata for documentation purposes.
#

description = """
The *ORCID Link Service* provides an API to enable the creation of an interface for a KBase
 user to link their KBase account to their ORCID account.

Once connected, *ORCID Link* enables certain integrations, including:

- syncing your KBase profile from your ORCID profile
- creating and managing KBase public Narratives within your ORCID profile 
"""

tags_metadata = [
    {
        "name": "misc",
        "description": "Miscellaneous operations"},
    {
        "name": "link",
        "description": "Add and remove KBase-ORCID linking; includes OAuth integration and API",
    },
    {
        "name": "orcid",
        "description": "Direct access to ORCID via ORCID Link"
    },
    {
        "name": "works",
        "description": "Add, remove, update 'works' records for a user's ORCID Account",
    },
]

# TODO: add fancy FastAPI configuration https://fastapi.tiangolo.com/tutorial/metadata/
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="ORCID Link Service",
    description=description,
    terms_of_service="https://www.kbase.us/about/terms-and-conditions-v2/",
    contact={
        "name": "KBase, Lawrence Berkeley National Laboratory, DOE",
        "url": "https://www.kbase.us",
        "email": "engage@kbase.us",
    },
    license_info={
        "name": "The MIT License",
        "url": "https://github.com/kbase/kb_sdk/blob/develop/LICENSE.md",
    },
    openapi_tags=tags_metadata,
)

#
# All paths are included here as routers. Each router is defined in the "routers" directory.
#
app.include_router(link.router)
app.include_router(linking_sessions.router)
app.include_router(works.router)
app.include_router(orcid.router)


#
# Custom exception handlers.
# Exceptions caught by FastAPI result in a variety of error responses, using
# a specific JSON format. However, we want to return all errors using our
# error format, which mimics JSON-RPC 2.0 and is compatible with the way
# our JSON-RPC 1.1 APIs operate (though not wrapped in an array).
#

# Have this return JSON in our "standard", or at least uniform, format. We don't
# want users of this api to need to accept FastAPI/Starlette error format.
# These errors are returned when the API is misused; they should not occur in production.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        "requestParametersInvalid",
        "Request Parameters Invalid",
        "This request does not comply with the schema for this endpoint",
        data={
            "detail": exc.errors(),
            "body": exc.body
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


#
# It is nice to let these exceptions propagate all the way up by default. There
# are many calls to auth, and catching each one just muddles up the code.
#
# @app.exception_handler(KBaseAuthMissingToken)
# async def kbase_auth_exception_handler(request: Request, exc: KBaseAuthMissingToken):
#     # TODO: this should reflect the nature of the auth error,
#     # probably either 401, 403, or 500.
#     return exception_error_response(
#         "missingToken", "Error authenticating with KBase", exc, status_code=401
#     )


@app.exception_handler(KBaseAuthInvalidToken)
async def kbase_auth_exception_handler(request: Request, exc: KBaseAuthMissingToken):
    # TODO: this should reflect the nature of the auth error,
    # probably either 401, 403, or 500.
    return exception_error_response(
        "invalidToken", "KBase auth token is invalid", exc, status_code=401
    )


@app.exception_handler(KBaseAuthException)
async def kbase_auth_exception_handler(request: Request, exc: KBaseAuthMissingToken):
    # TODO: this should reflect the nature of the auth error,
    # probably either 401, 403, or 500.
    return exception_error_response(
        "authError", "Unknown error authenticating with KBase", exc, status_code=500
    )


@app.exception_handler(ErrorException)
async def kbase_error_exception_handler(request: Request, exc: ErrorException):
    return exc.get_response()


# Raised by httpx for "raise_for_error"
# raise_for_error() is not used in the codebase, but let us keep this
# for a minute.
# @app.exception_handler(httpx.HTTPError)
# async def kbase_http_error_exception_handler(request: Request, exc: httpx.HTTPError):
#     # TODO: this should reflect the nature of the auth error,
#     # probably either 401, 403, or 500.
#     return exception_error_response(
#         "httpError", "General HTTP Error (httpx)", exc, status_code=exc.status_code
#     )


#
# This catches good ol' internal server errors. These are primarily due to internal programming
# logic errors. The reason to catch them here is to override the default FastAPI
# error structure.
#
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    return exception_error_response(
        "internalServerError",
        "Internal Server Error",
        exc,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


#
# Finally there are some other errors thrown by FastAPI which need overriding to return
# a normalized JSON form.
# This should be all of them.
# See: https://fastapi.tiangolo.com/tutorial/handling-errors/
#
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return error_response(
            "notFound",
            "Not Found",
            "The requested resource was not found",
            data={"detail": exc.detail, "path": request.url.path},
            status_code=404,
        )

    return error_response(
        "fastapiError",
        "FastAPI Error",
        "Internal FastAPI Exception",
        data={"detail": exc.detail},
        status_code=exc.status_code,
    )


################################
# API
################################


##
# /status - The status of the service.
#

# Also, most services and all KB-SDK apps have a /status endpoint.
# As a side benefit, it also returns non-private configuration.
# TODO: perhaps non-private configuration should be accessible via an
# "/info" endpoint.
#


STARTED = epoch_time_millis()


@app.get("/status", response_model=StatusResponse, tags=["misc"])
async def get_status():
    """
    The status of the service.

    The intention of this endpoint is as a lightweight way to call to ping the
    service, e.g. for health check, latency tests, etc.
    """
    return StatusResponse(
        status="ok",
        start_time=STARTED,
        time=epoch_time_millis())


@app.get("/info", response_model=InfoResponse, tags=["misc"])
async def get_info():
    """
    Returns basic information about the service and its runtime configuration.
    """
    kbase_sdk_config = get_kbase_config()
    config_copy = config().dict()
    config_copy['module']['CLIENT_ID'] = "REDACTED"
    config_copy['module']['CLIENT_SECRET'] = "REDACTED"
    return {"kbase_sdk_config": kbase_sdk_config, "config": config_copy}
    # result = InfoResponse(
    #     kbase_sdk_config=kbase_sdk_config,
    #     config=ensure_config()
    # )
    # return result.dict(exclude={'config': {'env': {'CLIENT_ID', 'CLIENT_SECRET'}}})


# Docs


@app.get("/docs", include_in_schema=True, tags=["misc"])
async def custom_swagger_ui_html(req: Request):
    """
    Provides a web interface to the auto-generated API docs.
    """
    root_path = get_service_path()
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )


#
# Redirection target for linking.
#
# The provided "code" is very short-lived and must be exchanged for the
# long-lived tokens without allowing the user to dawdle over it.
#
# Yet we do want the user to verify the linking with full account info first.
# Even using the forced logout during ORCID authentication, the ORCID interface
# does not identify the account after login. Since their user ids are cryptic,
#
# it would be possible on a multi-user computer to use the wrong ORCID Id.
# So what we do is save the response and issue our own temporary token.
# Upon submitting that token to /finish-link link is made.
#
@app.get(
    "/continue-linking-session",
    responses={
        302: {"description": "Redirect to the continuation page; or error page"}
    },
    tags=["link"],
)
async def continue_linking_session(
        request: Request,
        kbase_session: str = Cookie(default=None, description="KBase auth token taken from a cookie"),
        kbase_session_backup: str = Cookie(default=None, description="KBase auth token taken from a cookie"),
        code: str | None = None,
        state: str | None = None,
        error: str | None = None
):
    """
    The redirect endpoint for the ORCID OAuth flow we use for linking.
    """
    # Note that this is the target for redirection from ORCID,
    # and we don't have an Authorization header. We don't
    # (necessarily) have an auth cookie.
    # So we use the state to get the session id.
    if kbase_session is None:
        if kbase_session_backup is None:
            # TODO: this should be our own exception, otherwise it will be caught by
            # the global fastapi hooks.
            raise HTTPException(401, "Linking requires authentication")
        else:
            authorization = kbase_session_backup
    else:
        authorization = kbase_session

    if error is not None:
        return ui_error_response("link.orcid_error", "ORCID Error Linking", error)

    if code is None:
        return ui_error_response(
            "link.code_missing",
            "Linking code missing",
            "The 'code' query param is required but missing",
        )

    if state is None:
        return ui_error_response(
            "link.state_missing",
            "Linking state missing",
            "The 'state' query param is required but missing",
        )

    unpacked_state = json.loads(state)

    if "session_id" not in unpacked_state:
        return ui_error_response(
            "link.session_id_missing",
            "Linking Error",
            "The 'session_id' was not provided in the 'state' query param",
        )

    session_id = unpacked_state.get("session_id")

    session_record = get_linking_session_record(session_id, authorization)

    #
    # Exchange the temporary token from ORCID for the authorized token.
    #
    header = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    # Note that the redirect uri below is just for the api - it is not actually used
    # for redirection in this case.
    # TODO: investigate and point to the docs, because this is weird.
    # TODO: put in orcid client!
    data = {
        "client_id": config().module.CLIENT_ID,
        "client_secret": config().module.CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{get_service_url()}/continue-linking-session",
    }
    response = httpx.post(
        f'{config().orcid.oauthBaseURL}/token', headers=header, data=data
    )
    orcid_auth = ORCIDAuth.parse_obj(json.loads(response.text))

    #
    # Now we store the response from ORCID in our session.
    # We still need the user to finalize the linking, now that it has succeeded
    # which is done in finalize-linking-session.
    #

    # Note that this is approximate, as it uses our time, not the
    # ORCID server time.
    # session_record.orcid_auth = orcid_auth
    model = storage_model()
    model.update_linking_session_to_finished(session_id, orcid_auth)

    #
    # Redirect back to the orcidlink interface, with some
    # options that support integration into workflows.
    #
    params = {}

    if session_record.return_link is not None:
        params["return_link"] = session_record.return_link

    params["skip_prompt"] = session_record.skip_prompt

    return RedirectResponse(
        f"{config().kbase.uiOrigin}?{urlencode(params)}#orcidlink/continue/{session_id}",
        status_code=302,
    )
