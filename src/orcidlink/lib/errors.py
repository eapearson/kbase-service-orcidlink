from typing import Any, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse


class ErrorCode(BaseModel):
    code: str
    title: str
    description: str
    status_code: Optional[int]


REQUEST_PARAMETERS_INVALID = ErrorCode(
    code="requestParametersInvalid",
    title="Request Parameters Invalid",
    description="The request parameters (path, query, cooke) does not comply with the schema. "
    + "This indicates a mis-use of the API and should typically only be encountered "
    + "during development",
    status_code=422,
)

INVALID_TOKEN = ErrorCode(
    code="invalidToken",
    title="Invalid Token",
    description="Converted from an auth client exception, which in turn is in response to the auth "
    + "service reporting an invalid token",
    status_code=401,
)

INTERNAL_SERVER_ERROR = ErrorCode(
    code="internalServerError",
    title="Internal Server Error",
    description="The good ol generalized internal server error, meaning that something unexpected "
    + "broke within the codebase and cannot be (or at least is not) handled any better "
    + "or more specifically.",
    status_code=500,
)

NOT_FOUND = ErrorCode(
    code="notFound",
    title="Not Found",
    description="The resource or some component of it could not be located. We define this ourselves "
    + "since we want to return ALL errors in our error structure.",
    status_code=404,
)

FASTAPI_ERROR = ErrorCode(
    code="fastapiError",
    title="FastAPI Error",
    description="Some other error raised by FastAPI. We let the raised error determine the status code.",
    status_code=None,
)


#
#
# XXX = ErrorCode(
#     id="",
#     description="",
#     status_code=123
# )


# errors = {
#     "requestParametersInvalid": {
#         "description": "The request parameters (path, query, cooke) does not comply with the schema. "
#                        + "This indicates a mis-use of the API and should typically only be encountered "
#                        + "during development",
#         "status_code": 422,
#     },
#     "invalidToken": {
#         "description": "Converted from an auth client exception, which in turn is in response to the auth "
#                        + "service reporting an invalid token",
#         "statusCode": 401,
#     },
#     "internalServerError": {
#         "description": "The good ol generalized internal server error, meaning that something unexpected "
#                        + "broke within the codebase and cannot be (or at least is not) handled any better "
#                        + "or more specifically.",
#         "statusCode": 500,
#     },
#     "notFound": {
#         "description": "The resource or some component of it could not be located. We define this ourselves "
#                        + "since we want to return ALL errors in our error structure.",
#         "statusCode": 404,
#     },
#     "fastapiError": {
#         "description": "Some other error raised by FastAPI. We let the raised error determine the status code.",
#         # TODO: is this a good idea? Perhaps we should always raise a 500 and document the original status
#         # code in the data?
#         "statusCode": None,
#     },
# }


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


class ServiceErrorX(Exception):
    """
    An exception wrapper for an ErrorResponse and status_code.

    This is the exception to throw if you want to specify the
    specific error response.
    """

    code: str
    title: str
    description: str
    status_code: Optional[int]

    def __init__(
        self,
        code: str,
        title: str,
        message: str,
        data: Any = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.code = code
        self.title = title
        self.message = message
        self.data = data
        self.status_code = status_code

    def get_response(self) -> JSONResponse:
        content = {"code": self.code, "title": self.title, "message": self.message}
        if self.data is not None:
            content["data"] = self.data
        return JSONResponse(status_code=self.status_code or 500, content=content)


class InternalError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("internalError", "Internal Error", message, data, 500)


class NotFoundError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("notFound", "Not Found", message, data, 404)


class UnauthorizedError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("notAuthorized", "Not Authorized", message, data, 403)


class AuthTokenRequiredError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("authTokenRequired", "Auth Token Required", message, data, 401)


class UpstreamError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("upstreamError", "Upstream Error", message, data, 502)


class InvalidStateError(ServiceErrorX):
    def __init__(self, message: str, data: Any = None):
        super().__init__("invalidState", "Invalid State", message, data, 400)
