from typing import Dict, Generic, Literal, Optional, TypeVar

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel

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
    1061,
    1070,
    1080,
    1081,
    1082,
    1099,
]


class ErrorCode2(ServiceBaseModel):
    code: ErrorCode = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    status_code: int = Field(...)


class Errors(ServiceBaseModel):
    already_linked: ErrorCode2 = Field(...)
    authorization_required: ErrorCode2 = Field(...)
    not_authorized: ErrorCode2 = Field(...)
    not_found: ErrorCode2 = Field(...)
    internal_server_error: ErrorCode2 = Field(...)
    json_decode_error: ErrorCode2 = Field(...)
    content_type_error: ErrorCode2 = Field(...)
    upstream_error: ErrorCode2 = Field(...)
    upstream_jsonrpc_error: ErrorCode2 = Field(...)
    upstream_orcid_error: ErrorCode2 = Field(...)
    fastapi_error: ErrorCode2 = Field(...)
    request_validation_error: ErrorCode2 = Field(...)
    orcid_profile_name_private: ErrorCode2 = Field(...)
    linking_session_continue_invalid_param: ErrorCode2 = Field(...)
    linking_session_error: ErrorCode2 = Field(...)
    linking_session_already_linked_orcid: ErrorCode2 = Field(...)
    impossible_error: ErrorCode2 = Field(...)


ERRORS = Errors(
    already_linked=ErrorCode2(
        code=1000,
        title="FastAPI Error",
        description=(
            "Some other error raised by FastAPI. We let the raised error "
            "determine the status code."
        ),
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
        code=1061, title="Request Validation Error", description="", status_code=400
    ),
    orcid_profile_name_private=ErrorCode2(
        code=1070,
        title="ORCID Profile Name is Private",
        description="",
        status_code=400,
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
        status_code=400,
    ),
    impossible_error=ErrorCode2(
        code=1099, title="Impossible Error", description="", status_code=500
    ),
)

ERRORS_MAP: Dict[int, ErrorCode2] = {}

for field in Errors.model_fields.keys():
    error = getattr(ERRORS, field)
    ERRORS_MAP[error.code] = error

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
        description=(
            "A human-readable title for this error; displayable as an error "
            "dialog title"
        ),
    )
    message: str = Field(
        description=(
            "A human-readable error message, meant to be displayed to an end "
            "user or developer"
        ),
    )
    data: Optional[DataType] = Field(default=None)
