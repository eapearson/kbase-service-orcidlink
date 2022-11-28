# from fastapi import HTTPException
import json
from traceback import extract_tb
from urllib.parse import urlencode

import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lib.config import get_config


def error_response(code, message, data=None, status_code=400):
    detail = {
        "code": code,
        "message": message,
    }
    if data is not None:
        detail['data'] = data

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(detail)
    )


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


def ui_error_response(message: str):
    params = {"message": message}
    return fastapi.responses.RedirectResponse(
        f"{get_config(['kbase', 'baseURL'])}?message={urlencode(json.dumps(params))}#orcidlink/error)",
        status_code=302,
    )
