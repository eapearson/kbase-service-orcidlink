from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from orcidlink.lib.config import config
from orcidlink.lib.responses import (
    ErrorException,
    error_response,
    error_response_not_found,
    exception_error_response,
)
from orcidlink.routers import link, linking_sessions, orcid, root, works
from orcidlink.service_clients.KBaseAuth import (
    KBaseAuthException,
    KBaseAuthInvalidToken,
    KBaseAuthMissingToken,
)
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
    {"name": "misc", "description": "Miscellaneous operations"},
    {
        "name": "link",
        "description": "Add and remove KBase-ORCID linking; includes OAuth integration and API",
    },
    {"name": "orcid", "description": "Direct access to ORCID via ORCID Link"},
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
app.include_router(root.router)
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
        data={"detail": exc.errors(), "body": exc.body},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


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
async def kbase_auth_invalid_token_handler(
        request: Request, exc: KBaseAuthMissingToken
):
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
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


@app.get(
    "/docs",
    include_in_schema=True,
    tags=["misc"],
    responses={
        200: {"description": "Successfully returned the api docs"},
        302: {"description": "Not configured; should never occur"},
    },
)
async def docs(req: Request):
    """
    Provides a web interface to the auto-generated API docs.
    """
    if app.openapi_url is None:
        # FastAPI is obstinate - I initially wanted to handle this case
        # with a "redirect error" to kbase-ui, but even though I regurned
        # 302, it resulted in a 404 in tests! I don't know about real life.
        # So lets just make this a 404, which is reasonable in any case.
        return error_response_not_found("The 'openapi_url' is 'None'")

        # response = ui_error_response(
        #     "docs.no_url",
        #     "No DOCS URL",
        #     "The 'openapi_url' is 'None'",
        # )
        # print('RESPONSE IS', response.status_code)
        # return response

    openapi_url = config().services.ORCIDLink.url + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )
