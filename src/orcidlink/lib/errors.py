from dataclasses import dataclass, fields

# from fastapi import HTTPException
from typing import Dict, Generic, Literal, Optional, TypeVar

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel


@dataclass
class ErrorCodeX:
    code: str
    title: str
    description: str
    status_code: int


ErrorCode = Literal[
    1000,
    1010,
    1011,
    1020,
    1030,
    1040,
    1041,
    1050,
    1051,
    1052,
    1060,
    1070,
    1080,
    1081,
    1082,
    1099,
]


@dataclass
class ErrorCode2:
    code: ErrorCode
    title: str
    description: str
    status_code: int


@dataclass
class Errors:
    already_linked: ErrorCode2
    authorization_required: ErrorCode2
    not_authorized: ErrorCode2
    not_found: ErrorCode2
    internal_server_error: ErrorCode2
    json_decode_error: ErrorCode2
    content_type_error: ErrorCode2
    upstream_error: ErrorCode2
    upstream_jsonrpc_error: ErrorCode2
    upstream_orcid_error: ErrorCode2
    fastapi_error: ErrorCode2
    request_validation_error: ErrorCode2
    linking_session_continue_invalid_param: ErrorCode2
    linking_session_error: ErrorCode2
    linking_session_already_linked_orcid: ErrorCode2
    impossible_error: ErrorCode2


ERRORS = Errors(
    already_linked=ErrorCode2(
        code=1000,
        title="FastAPI Error",
        description="Some other error raised by FastAPI. We let the raised error determine the status code.",
        status_code=400,
    ),
    authorization_required=ErrorCode2(
        code=1010, title="Authorization Required", description="", status_code=401
    ),
    not_authorized=ErrorCode2(
        code=1011, title="Not Authorized", description="", status_code=403
    ),
    not_found=ErrorCode2(code=1020, title="Not Found", description="", status_code=404),
    internal_server_error=ErrorCode2(
        code=1030, title="Internal Server Error", description="", status_code=500
    ),
    json_decode_error=ErrorCode2(
        code=1040, title="Error Decoding Response", description="", status_code=502
    ),
    content_type_error=ErrorCode2(
        code=1041,
        title="Received Incorrect Content Type",
        description="",
        status_code=502,
    ),
    upstream_error=ErrorCode2(
        code=1050, title="Upstream Error", description="", status_code=502
    ),
    upstream_jsonrpc_error=ErrorCode2(
        code=1051, title="Upstream JSON-RPC Error", description="", status_code=502
    ),
    upstream_orcid_error=ErrorCode2(
        code=1052, title="Upstream ORCID Error", description="", status_code=502
    ),
    fastapi_error=ErrorCode2(
        code=1060, title="FastAPI Error", description="", status_code=400
    ),
    request_validation_error=ErrorCode2(
        code=1070, title="Request Validation Error", description="", status_code=400
    ),
    linking_session_continue_invalid_param=ErrorCode2(
        code=1080,
        title="Linking Session Continue Redirect Missing Parameter",
        description="",
        status_code=502,
    ),
    linking_session_error=ErrorCode2(
        code=1081, title="ORCID Error Linking", description="", status_code=502
    ),
    linking_session_already_linked_orcid=ErrorCode2(
        code=1082, 
        title="ORCID account already linked", 
        description="""
The ORCID account requested for linking is already linked to another KBase account. 
        """, 
        status_code=400
    ),
    impossible_error=ErrorCode2(
        code=1099, title="Impossible Error", description="", status_code=500
    ),
)

ERRORS_MAP: Dict[int, ErrorCode2] = {}

for field in fields(ERRORS):
    error = getattr(ERRORS, field.name)
    ERRORS_MAP[error.code] = error


# REQUEST_PARAMETERS_INVALID = ErrorCode(
#     code="requestParametersInvalid",
#     title="Request Parameters Invalid",
#     description="The request parameters (path, query, cooke) does not comply with the schema. "
#     + "This indicates a mis-use of the API and should typically only be encountered "
#     + "during development",
#     status_code=422,
# )

# INVALID_TOKEN = ErrorCode(
#     code="invalidToken",
#     title="Invalid Token",
#     description="Converted from an auth client exception, which in turn is in response to the auth "
#     + "service reporting an invalid token",
#     status_code=401,
# )

# TOKEN_REQUIRED_BUT_MISSING = ErrorCode(
#     code="authorizationRequired",
#     title="Authorization Required",
#     description="The resource requires authorization, but not is present ",
#     status_code=401,
# )

# ORCID_INVALID_TOKEN = ErrorCode(
#     code="orcidInvalidToken",
#     title="ORCID Invalid Token",
#     description="""
# Converted from an the ORCID API client exception, which in turn is in response to ORCID
# api reporting an invalid token. In all probability, this is due to the user having removed
# access for KBase.
# """,
#     status_code=401,
# )

# INTERNAL_SERVER_ERROR = ErrorCode(
#     code="internalServerError",
#     title="Internal Server Error",
#     description="The good ol generalized internal server error, meaning that something unexpected "
#     + "broke within the codebase and cannot be (or at least is not) handled any better "
#     + "or more specifically.",
#     status_code=500,
# )

NOT_FOUND = ErrorCodeX(
    code="notFound",
    title="Not Found",
    description="The resource or some component of it could not be located. We define this ourselves "
    + "since we want to return ALL errors in our error structure.",
    status_code=404,
)

FASTAPI_ERROR = ErrorCodeX(
    code="fastapiError",
    title="FastAPI Error",
    description="Some other error raised by FastAPI. We let the raised error determine the status code.",
    status_code=500,
)

# CONTENT_TYPE_ERROR = ErrorCode(
#     code="badContentType",
#     title="Received Incorrect Content Type",
#     description="Expected application/json for a json response",
#     status_code=502,
# )

# JSON_DECODE_ERROR = ErrorCode(
#     code="jsonDecodeError",
#     title="Error Decoding Response",
#     description="An error was encountered parsing, or decoding, the JSON response string",
#     status_code=502,
# )

#
# A call to a KBase service resulted in an unhandled error.
# It is expected that some errors are somewhat "normal", or at least common enough that we
# may want to recognize them in the server.
# However, under normal conditions errors from apis are simply not expected, and can only be
# propagated out, back to the client (probably web browser) which can display and report them.
# The error should have the entire JSON-RPC error structure included in the "data" property
# named "error".
#
# UPSTREAM_JSONRPC_ERROR = ErrorCode(
#     code="upstreamJSONRPCError",
#     title="Error Reported by an Upstream KBase SErvice",
#     description="An error was encountered in an upstream service.",
#     status_code=502,
# )

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


# class ServiceError(Exception):
#     """
#     An exception wrapper for an ErrorResponse and status_code.

#     This is the exception to throw if you want to specify the
#     specific error response.
#     """

#     error: Any
#     status_code: int

#     def __init__(self, error: Any, status_code: int):
#         super().__init__(error.message)
#         self.error = error
#         self.status_code = status_code

#     def get_response(self) -> JSONResponse:
#         return JSONResponse(
#             status_code=self.status_code,
#             content=jsonable_encoder(self.error, exclude_unset=True),
#         )


# class ServiceErrorXX(Exception):
#     """
#     An exception wrapper for an ErrorResponse and status_code.

#     This is the exception to throw if you want to specify the
#     specific error response.
#     """

#     error_code: ErrorCode

#     def __init__(
#         self, error_code: ErrorCode, message: str, data: JSONLikeObject | None = None
#     ):
#         super().__init__(message)
#         self.message = message
#         self.error_code = error_code
#         self.data = data

#     def get_response(self) -> JSONResponse:
#         content = asdict(self.error_code)
#         # We always supply this data
#         data = {
#             "description": self.error_code.description,
#             "status_code": self.error_code.status_code,
#         }
#         # Add more data ...
#         if self.data is not None:
#             data.update(self.data)

#         content = {
#             "message": self.message,
#             "code": self.error_code.code,
#             "data": data,
#         }
#         content["message"] = self.message
#         return JSONResponse(status_code=self.error_code.status_code, content=content)

# def content_type_error(cte: aiohttp.ContentTypeError):
#     data: JSONLikeObject = {}

#     if cte.headers is not None:
#         data["originalContentType"] = cte.headers["content-type"]

#     return ServiceErrorXX(
#         JSON_DECODE_ERROR,
#         f"Expected a JSON content type",
#         data=data)

# def json_decode_error(jde: json.JSONDecodeError):
#     return ServiceErrorXX(
#         JSON_DECODE_ERROR,
#         f"Expected a JSON response",
#         data={"decodeErrorMessage": str(jde)}, )

# def internal_server_error(ex: Exception):
#     return ServiceErrorXX(
#         INTERNAL_SERVER_ERROR,
#         f"Unexpected exception",
#         data={"exceptionMessage": str(ex)},
#     )

# def upstream_jsonrpc_error(error: JSONRPCError):
#     data: JSONLikeObject = {
#         "error": {
#             "code": error.code,
#             "message": error.message,
#             "data": error.data
#         }
#     }

#     return ServiceErrorXX(
#         UPSTREAM_JSONRPC_ERROR,
#         f"Error in upstream KBase service",
#         data=data,
#     )


# Standard JSON-RPC 2.0 errors

# See: https://www.jsonrpc.org/specification#error_object
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR_MIN = -32000
SERVER_ERROR_MAX = -32099

# Our own errors.
# TODO

#
# A type variable to represent some data to be sent in the error response, based
# on ServiceBaseModel so both validated and with json representation -- just what
# we need :)
#
DataType = TypeVar("DataType", bound=ServiceBaseModel)


class ErrorResponse(ServiceBaseModel, Generic[DataType]):
    """
    A generic error object used for all error responses.

    See [the error docs](docs/errors.md) for more information.
    """

    # see lib/errors.py for all available error codes.
    code: ErrorCode = Field(
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
    data: Optional[DataType] = Field(default=None)
