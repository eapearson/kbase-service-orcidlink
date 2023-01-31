# from fastapi import HTTPException
from traceback import extract_tb
from typing import Any, Dict, Generic, Mapping, Optional, TypeVar, Union
from urllib.parse import urlencode

from fastapi import Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib.config import config
from pydantic import BaseModel, Field

##
# Common http responses, implemented as response-generating functions.
#

T = TypeVar("T", bound=BaseModel)


class ErrorResponse(BaseModel, Generic[T]):
    """
    A generic error object used for all error responses.

    See [the error docs](docs/errors.md) for more information.
    """

    # see lib/errors.py for all available error codes.
    code: str = Field(
        min_length=5,
        max_length=25,
        description="A unique code associated with this specific type of error",
    )
    title: str = Field(
        min_length=5,
        max_length=50,
        description="A human-readable title for this error; displayable as an error dialog title",
    )
    message: str = Field(
        description="A human-readable error message, meant to be displayed to an end user or developer",
    )
    data: Optional[T] = Field(default=None)


def success_response_no_data() -> Response:
    return Response(status_code=204)


def error_response(
    code: str,
    title: str,
    message: str,
    data: Any = None,
    status_code: int = 400,
) -> JSONResponse:
    response = ErrorResponse[Any](
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
    return error_response("notFound", "Not Found", message, status_code=404)


def exception_error_response(
    code: str,
    title: str,
    exception: Exception,
    data: Optional[Any] = None,
    status_code: int = 400,
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

    response = ErrorResponse[Any](
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
