from typing import Dict, List

from fastapi_jsonrpc import BaseError
from pydantic import Field

from orcidlink.lib.json_support import JSONObject
from orcidlink.lib.type import ServiceBaseModel


class JSONRPCError(BaseError):
    CODE: int
    MESSAGE: str
    data: JSONObject


class AlreadyLinkedError(JSONRPCError):
    CODE = 1000
    MESSAGE = "User already linked"


class AuthorizationRequiredError(JSONRPCError):
    CODE = 1010
    MESSAGE = "Authorization Required"


class NotAuthorizedError(JSONRPCError):
    CODE = 1011
    MESSAGE = "Not Authorized"


class NotFoundError(JSONRPCError):
    CODE = 1020
    MESSAGE = "Not Found"


class JSONDecodeError(JSONRPCError):
    CODE = 1040
    MESSAGE = "Error decoding JSON response"


class ContentTypeError(JSONRPCError):
    CODE = 1041
    MESSAGE = "Received Incorrect Content Type"


#
# ORCID or other upstream errors that we cannot or choose not to
# handle with specificity.
#


class UpstreamError(JSONRPCError):
    CODE = 1050
    MESSAGE = "Upstream Error"


#
# This is not really an ORCID Error, but related to an orcid record. We need
# to be able to catch this condition - in which the user has overly restricted
# the name field, and KBase cannot access it for display
#
# TODO: Check if we need this, or if we can just detected that the name is
# absent or None.
#


class ORCIDProfileNamePrivate(JSONRPCError):
    CODE = 1100
    MESSAGE = "ORCID Profile has name set to private"


#
# ORCID Errors that we can do something with
#


class ORCIDInsufficientAuthorizationError(JSONRPCError):
    CODE = 1101
    MESSAGE = "ORCID insufficient authorization"


class ORCIDNotFoundError(JSONRPCError):
    CODE = 1102
    MESSAGE = "Something not found at ORCID"


class ORCIDNotAuthorizedError(JSONRPCError):
    CODE = 1103
    MESSAGE = "ORCID no authorization"


# Standard JSON-RPC 2.0 Errors

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR_MIN = -32000
SERVER_ERROR_MAX = -32099


class ErrorDescription(ServiceBaseModel):
    code: int = Field(...)
    message: str = Field(...)


ERRORS: List[ErrorDescription] = [
    ErrorDescription(code=-32700, message="Parse error"),
    ErrorDescription(code=-32600, message="Invalid request"),
    ErrorDescription(code=-32601, message="Method not found"),
    ErrorDescription(code=-32602, message="Invalid params"),
    ErrorDescription(code=-32603, message="Internal error"),
    ErrorDescription(code=1010, message="Authorization Required"),
    ErrorDescription(code=1011, message="Not Authorized"),
    ErrorDescription(code=1041, message="Received Incorrect Content Type"),
    ErrorDescription(code=1040, message="Error decoding JSON response"),
    ErrorDescription(code=1050, message="Upstream Error"),
    ErrorDescription(code=1020, message="Not Found"),
    ErrorDescription(code=1000, message="Already Linked"),
    ErrorDescription(code=1100, message="ORCID Profile has name set to private"),
    ErrorDescription(
        code=ORCIDInsufficientAuthorizationError.CODE,
        message=ORCIDInsufficientAuthorizationError.MESSAGE,
    ),
    ErrorDescription(code=ORCIDNotFoundError.CODE, message=ORCIDNotFoundError.MESSAGE),
]

ERRORS_MAP: Dict[int, ErrorDescription] = {}

for error in ERRORS:
    ERRORS_MAP[error.code] = error
