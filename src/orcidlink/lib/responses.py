# from fastapi import HTTPException
from traceback import extract_tb
from typing import Any, Dict, Mapping, Optional, Union
from urllib.parse import urlencode

from fastapi import Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib.config import config
from pydantic import BaseModel, Field


##
# Common http responses, implemented as response-generating functions.
#


class ErrorResponse(BaseModel):
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


def ensure_authorization(authorization: str | None) -> str:
    if authorization is None:
        raise ErrorException(
            error=ErrorResponse(
                code="missingToken",
                title="Missing Token",
                message="API call requires a KBase auth token",
            ),
            status_code=401,
        )
    return authorization


AUTHORIZATION_HEADER = Header(default=None, description="KBase auth token")

ResponseMapping = Mapping[Union[int, str], Dict[str, Any]]

AUTH_RESPONSES: ResponseMapping = {
    401: {"description": "KBase auth token absent"},
    403: {"description": "KBase auth token invalid"},
}

STD_RESPONSES: ResponseMapping = {
    422: {
        "description": "Either input or output data does not comply with the API schema",
        "model": ErrorResponse,
    }
}
