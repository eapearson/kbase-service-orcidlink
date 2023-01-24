# from fastapi import HTTPException
from traceback import extract_tb
from typing import Any, Dict, Mapping, Optional, Tuple, Union
from urllib.parse import urlencode

from fastapi import Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib.config import config
from orcidlink.service_clients.KBaseAuth import KBaseAuth, TokenInfo
from pydantic import BaseModel, Field


##
# Common http responses, implemented as response-generating functions.
#


class ErrorResponse(BaseModel):
    """
    A generic error object used for all error responses.

    See [the error docs](docs/errors.md) for more information.
    """

    code: str = Field(...)
    title: str = Field(...)
    message: str = Field(...)
    data: object = Field(None)


def success_response_no_data():
    return Response(status_code=204)


def make_error(code: str, title: str, message: str, data=None) -> ErrorResponse:
    response = ErrorResponse(
        code=code,
        title=title,
        message=message,
    )
    if data is not None:
        response.data = data

    return response


def error_response(
    code: str, title: str, message: str, data=None, status_code=400
) -> JSONResponse:
    response = ErrorResponse(
        code=code,
        title=title,
        message=message,
    )
    if data is not None:
        response.data = data

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response, exclude_unset=True)
    )


def error_response_not_found(message: str) -> JSONResponse:
    return error_response("not-found", "Not Found", message, status_code=404)


def exception_error_response(
    code: str,
    title: str,
    exception: Exception,
    data: Optional[dict] = None,
    status_code=400,
) -> JSONResponse:
    traceback = []
    for tb in extract_tb(exception.__traceback__):
        traceback.append(
            {
                "filename": tb.filename,
                "line_number": tb.lineno,
                "name": tb.name,
                "line": tb.line,
            }
        )

    if data is None:
        data = {}

    data.update({"exception": str(exception), "traceback": traceback})

    response = ErrorResponse(
        code=code or "exception",
        title=title or "Exception",
        message=str(exception),
        data=data,
    )

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response, exclude_unset=True)
    )


def ui_error_response(code: str, title: str, message: str) -> RedirectResponse:
    error_params = urlencode({"code": code, "title": title, "message": message})
    return RedirectResponse(
        f"{config().ui.origin}?{error_params}#orcidlink/error", status_code=302
    )


#
# Specific canned error responses.
#


class ErrorException(Exception):
    def __init__(self, error: ErrorResponse, status_code: int):
        super().__init__(error.message)
        self.error = error
        self.status_code = status_code

    def get_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content=jsonable_encoder(self.error, exclude_unset=True),
        )


def make_error_exception(
    code: str, title: str, message: str, data=None, status_code=400
) -> ErrorException:
    return ErrorException(
        error=make_error(code, title, message, data), status_code=status_code
    )


def ensure_authorization(authorization: str | None) -> Tuple[str, TokenInfo]:
    """
    Ensures that the "authorization" value, the KBase auth token, is
    not none. This is a convenience function for endpoints, whose sole
    purpose is to ensure that the provided token is good and valid.
    """
    if authorization is None:
        raise ErrorException(
            error=ErrorResponse(
                code="missingToken",
                title="Missing Token",
                message="API call requires a KBase auth token",
            ),
            status_code=401,
        )
    auth = KBaseAuth(
        auth_url=config().services.Auth2.url,
        cache_lifetime=int(config().services.Auth2.tokenCacheLifetime / 1000),
        cache_max_size=config().services.Auth2.tokenCacheMaxSize,
    )
    return authorization, auth.get_token_info(authorization)


AUTHORIZATION_HEADER = Header(
    # default=None,
    description="KBase auth token",
    min_length=32,
    max_length=32,
)

ResponseMapping = Mapping[Union[int, str], Dict[str, Any]]

AUTH_RESPONSES: ResponseMapping = {
    401: {"description": "KBase auth token absent or invalid", "model": ErrorResponse},
    # 403: {"description": "KBase auth token invalid", "model": ErrorResponse},
}

STD_RESPONSES: ResponseMapping = {
    422: {
        "description": "Input or output data does not comply with the API schema",
        "model": ErrorResponse,
    }
}
