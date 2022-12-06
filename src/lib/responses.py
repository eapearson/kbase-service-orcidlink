# from fastapi import HTTPException
import json
from traceback import extract_tb
from typing import Any
from urllib.parse import urlencode

import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from lib.config import get_config


class ErrorResponse(BaseModel):
    code: str = Field(...)
    title: str = Field(...)
    message: str = Field(...)
    data: object = Field(None)

def success_response_no_data():
    return Response(status_code=204)

def make_error(code: str, title: str, message: str, data=None):
    error_response = ErrorResponse(
        code=code,
        title=title,
        message=message,
    )
    if data is not None:
        error_response.data = data

    return error_response


def error_response(code: str, title: str, message: str, data=None, status_code=400):
    error_response = ErrorResponse(
        code=code,
        title=title,
        message=message,
    )
    if data is not None:
        error_response.data = data

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error_response, exclude_unset=True)
    )

def exception_error_response(code: str, title: str, exception: Exception, data=None, status_code=400):
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

    error_response = ErrorResponse(
        code=code,
        title=title,
        message=str(exception),
        data=data
    )

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(error_response, exclude_unset=True)
    )

def exception_error(exception, code=None, title=None, message=None, data=None):
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

def exception_response(exception, data=None):
    error_response =exception_error(exception, data)
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(error_response, exclude_unset=True)
    )


def make_error_field(name: str, value: str):
    return f"{name}={urlencode(value)}"


def make_error_params(code: str, title: str, message: str):
    return "&".join([
        make_error_field("code", code),
        make_error_field("title", title),
        make_error_field("message", message)
    ])
 

def ui_error_response(code: str, title: str, message: str):
    error_params = make_error_params(code, title, message)
    return fastapi.responses.RedirectResponse(
        f"{get_config(['kbase', 'uiOrigin'])}?{error_params}#orcidlink/error)",
        status_code=302
    )

# 
# Specific canned error responses.
#


def auth_required_error_response():
    return error_response('unauthorized', 'Unauthorized',
                          'Authentication required via the "Authorization" header',
                          status_code=401)

class ErrorException(Exception):
    def __init__(self, error: ErrorResponse, status_code: int):
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


def ensure_authorization(authorization: str) -> str:
    if authorization is None:
        raise ErrorException(
            error=ErrorResponse(
                code="missingToken",
                title="Unauthorized",
                message= "API call requires a KBase auth token"
            ),
            status_code=401
        )
    return authorization

def to_json(hopefully_jsonable: str):
    try: 
        return json.loads(hopefully_jsonable)
    except Exception as ex:
        raise ErrorException(
                exception_error(ex, code="parseError", title="Error Parsing JSON", message="An error was encountered parsing a string into a jsonable value"),
                500)
