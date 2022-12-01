# from fastapi import HTTPException
from traceback import extract_tb
from urllib.parse import urlencode

import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lib.config import get_config


def error_response(code: str, title: str, message: str, data=None, status_code=400):
    detail = {
        "code": code,
        "title": title,
        "message": message,
    }
    if data is not None:
        detail['data'] = data

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(detail)
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

    detail = {
        "code": code,
        "title": title,
        "message": str(exception),
        "data": data
    }

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(detail)
    )
    #
    # return error_response(
    #     'exception',
    #     'The service encountered an error which resulted in an Exception',
    #     status_code=500,
    #     data=data)


def exception_response(exception, data=None):
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

    return error_response(
        'exception',
        'The service encountered an error which resulted in an Exception',
        status_code=500,
        data=data)


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
