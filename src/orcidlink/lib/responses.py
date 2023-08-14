from traceback import extract_tb
from typing import Any, Dict, List, Mapping, Optional, Union
from urllib.parse import urlencode

from fastapi import Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import Field

from orcidlink.lib.errors import ErrorCode, ErrorCode2, ErrorResponse
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.runtime import config

##
# Common http responses, implemented as response-generating functions.
#


def error_response2(
    # response_content: ErrorResponse[ServiceBaseModel],
    response_content: Any,
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response_content, exclude_unset=True),
    )


#
# def error_response3(
#         error: ErrorCode
# ):
#     return JSONResponse(
#         status_code=error.status_code,
#         content=jsonable_encoder(error, exclude_unset=True)
#     )


def error_response(
    error: ErrorCode2,
    message: str,
    data: Optional[ServiceBaseModel] = None,
    status_code: int = 400,
) -> JSONResponse:
    response = ErrorResponse[ServiceBaseModel](
        code=error.code,
        title=error.title,
        message=message,
    )

    if data is not None:
        response.data = data

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response, exclude_unset=True)
    )


class ExceptionTraceback(ServiceBaseModel):
    filename: str = Field(...)
    line_number: Optional[int] = Field(
        default=None, validation_alias="line-number", serialization_alias="line-number"
    )
    name: str = Field(...)
    line: Optional[str] = Field(default=None)


class ExceptionData(ServiceBaseModel):
    exception: str = Field(...)
    traceback: List[ExceptionTraceback]


def exception_error_response(
    error: ErrorCode2,
    exception: Exception,
    status_code: int = 400,
) -> JSONResponse:
    traceback = []
    for tb in extract_tb(exception.__traceback__):
        traceback.append(
            ExceptionTraceback(
                filename=tb.filename, line_number=tb.lineno, name=tb.name, line=tb.line
            )
        )

    data = ExceptionData(exception=str(exception), traceback=traceback)

    response = ErrorResponse[Any](
        code=error.code,
        title=error.title or "Exception",
        message=str(exception),
        data=data,
    )

    return JSONResponse(
        status_code=status_code, content=jsonable_encoder(response, exclude_unset=True)
    )


def ui_error_response(error: ErrorCode2, message: str) -> RedirectResponse:
    error_params = urlencode(
        {"code": error.code, "title": error.title, "message": message}
    )
    return RedirectResponse(
        f"{config().ui_origin}?{error_params}#orcidlink/error", status_code=302
    )


#
# Specific canned error responses.
#


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
