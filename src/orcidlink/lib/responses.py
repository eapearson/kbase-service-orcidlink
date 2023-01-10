# from fastapi import HTTPException
import json
from traceback import extract_tb
from urllib.parse import urlencode

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib.config import get_config
from pydantic import BaseModel, Field


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


def error_response(code: str, title: str, message: str, data=None, status_code=400) -> JSONResponse:
    response = ErrorResponse(
        code=code,
        title=title,
        message=message,
    )
    if data is not None:
        response.data = data

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response, exclude_unset=True)
    )


def make_error_response_from_exception(exception, code: str = None, title: str = None,
                                       message: str = None, data: dict = None):
    traceback = []
    for tb in extract_tb(exception.__traceback__):
        traceback.append({
            'filename': tb.filename,
            'line_number': tb.lineno,
            'name': tb.name,
            'line': tb.line
        })

    if data is None:
        data = {}

    data.update({
        'exception': str(exception),
        'traceback': traceback
    })

    return ErrorResponse(
        code=code or 'exception',
        title=title or 'Exception',
        message=message or str(exception),
        data=data
    )


def exception_error_response(code: str, title: str, exception: Exception,
                             data: dict = {},
                             status_code=400) -> JSONResponse:
    response = make_error_response_from_exception(exception, code=code, title=title, data=data)

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response, exclude_unset=True)
    )


def ui_error_response(code: str, title: str, message: str) -> RedirectResponse:
    error_params = urlencode({
        "code": code,
        "title": title,
        "message": message
    })
    return RedirectResponse(
        f"{get_config(['kbase', 'uiOrigin'])}?{error_params}#orcidlink/error",
        status_code=302
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
            content=jsonable_encoder(self.error, exclude_unset=True)
        )


def make_error_exception(code: str, title: str, message: str, data=None, status_code=400) -> ErrorException:
    return ErrorException(
        error=make_error(code, title, message, data),
        status_code=status_code
    )


def ensure_authorization(authorization: str | None) -> str:
    if authorization is None:
        raise ErrorException(
            error=ErrorResponse(
                code="missingToken",
                title="Missing Token",
                message="API call requires a KBase auth token"
            ),
            status_code=401
        )
    return authorization


def text_to_jsonable(hopefully_jsonable: str):
    try:
        return json.loads(hopefully_jsonable)
    except Exception as ex:
        response = make_error_response_from_exception(
            ex,
            code="parseError",
            title="Error Parsing JSON",
            message="An error was encountered parsing a string into a jsonable value"
        )
        raise ErrorException(response, 500)
