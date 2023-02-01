from typing import Any

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

errors = {
    "requestParametersInvalid": {
        "description": "The request parameters (path, query, cooke) does not comply with the schema. "
        + "This indicates a mis-use of the API and should typically only be encountered "
        + "during development",
        "status_code": 422,
    },
    "invalidToken": {
        "description": "Converted from an auth client exception, which in turn is in response to the auth "
        + "service reporting an invalid token",
        "statusCode": 401,
    },
    "internalServerError": {
        "description": "The good ol generalized internal server error, meaning that something unexpected "
        + "broke within the codebase and cannot be (or at least is not) handled any better "
        + "or more specifically.",
        "statusCode": 500,
    },
    "notFound": {
        "description": "The resource or some component of it could not be located. We define this ourselves "
        + "since we want to return ALL errors in our error structure.",
        "statusCode": 404,
    },
    "fastapiError": {
        "description": "Some other error raised by FastAPI. We let the raised error determine the status code.",
        # TODO: is this a good idea? Perhaps we should always raise a 500 and document the original status
        # code in the data?
        "statusCode": None,
    },
}


class ServiceError(Exception):
    """
    An exception wrapper for an ErrorResponse and status_code.

    This is the exception to throw if you want to specify the
    specific error response.
    """

    error: Any
    status_code: int

    def __init__(self, error: Any, status_code: int):
        super().__init__(error.message)
        self.error = error
        self.status_code = status_code

    def get_response(self) -> JSONResponse:
        return JSONResponse(
            status_code=self.status_code,
            content=jsonable_encoder(self.error, exclude_unset=True),
        )
