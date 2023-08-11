import json
from typing import Any, Dict, Generic, Optional

import aiohttp
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import Field

from orcidlink.lib.errors import ERRORS, DataType, ErrorCode, ErrorCode2, ErrorResponse
from orcidlink.lib.json_file import JSONLikeObject
from orcidlink.lib.service_clients.jsonrpc import JSONRPCError
from orcidlink.lib.type import ServiceBaseModel


class ServiceErrorY(Exception):
    error: ErrorCode2
    message: str

    def __init__(
        self, error: ErrorCode2, message: str, data: Optional[DataType] = None
    ):
        super().__init__(message)
        self.message = message
        self.error = error
        self.data = data

    def get_response(self) -> JSONResponse:
        content: JSONLikeObject = {
            "code": self.error.code,
            "title": self.error.title,
            "message": self.message,
        }
        if self.data is not None:
            content["data"] = dict(self.data)
        return JSONResponse(status_code=self.error.status_code or 500, content=content)


# x = ServiceErrorY("foo",
#     status_code=100000,
#     error=ERRORS.impossible_error
# )


class ServiceErrorX(Exception):
    """
    An exception wrapper for an ErrorResponse and status_code.

    This is the exception to throw if you want to specify the
    specific error response.
    """

    code: int
    title: str
    description: str
    status_code: Optional[int]

    def __init__(
        self,
        code: int,
        title: str,
        message: str,
        data: Optional[ServiceBaseModel] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        self.code = code
        self.title = title
        self.message = message
        self.data = data
        self.status_code = status_code

    def get_response(self) -> JSONResponse:
        content: JSONLikeObject = {
            "code": self.code,
            "title": self.title,
            "message": self.message,
        }
        if self.data is not None:
            content["data"] = dict(self.data)
        return JSONResponse(status_code=self.status_code or 500, content=content)


# class ClientError(ServiceErrorX):
#     def __init__(self, status_code: int, message: str, data: Any = None):
#         super().__init__("clientError", "Client Error", message, data, status_code)


class AlreadyLinkedError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(
            ERRORS.already_linked.code,
            ERRORS.already_linked.title,
            message,
            status_code=400,
        )


class AuthorizationRequiredError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(
            ERRORS.authorization_required.code,
            ERRORS.authorization_required.title,
            message,
            status_code=401,
        )


class UnauthorizedError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(
            ERRORS.not_authorized.code,
            ERRORS.not_authorized.title,
            message,
            status_code=403,
        )


class NotFoundError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(1020, "Not Found", message, status_code=404)


class InternalServerError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(
            ERRORS.internal_server_error.code,
            ERRORS.internal_server_error.title,
            message,
            status_code=500,
        )


class JSONDecodeErrorData(ServiceBaseModel):
    decodeErrorMessage: str


class JSONDecodeError(ServiceErrorX):
    def __init__(self, message: str, jde: json.JSONDecodeError):
        data = JSONDecodeErrorData(decodeErrorMessage=str(jde))
        super().__init__(
            ERRORS.json_decode_error.code,
            ERRORS.json_decode_error.title,
            message,
            data=data,
            status_code=502,
        )


class ContentTypeErrorData(ServiceBaseModel):
    originalContentType: Optional[str] = Field(default=None)


class ContentTypeError(ServiceErrorX):
    data: ContentTypeErrorData

    def __init__(self, message: str, cte: aiohttp.ContentTypeError):
        data = ContentTypeErrorData()

        if cte.headers is not None:
            data.originalContentType = cte.headers["content-type"]

        super().__init__(
            ERRORS.content_type_error.code,
            ERRORS.content_type_error.title,
            message,
            data=data,
            status_code=502,
        )


class UpstreamErrorData(ServiceBaseModel):
    status_code: int
    source: str
    detail: Optional[Dict[str, Any]] = Field(default=None)
    message: Optional[str] = Field(default=None)


class UpstreamORCIDAPIError(ServiceErrorX):
    data: UpstreamErrorData

    def __init__(self, message: str, data: UpstreamErrorData):
        super().__init__(
            ERRORS.upstream_orcid_error.code,
            ERRORS.upstream_orcid_error.title,
            message,
            data,
            502,
        )


# def upstream_jsonrpc_error(error: JSONRPCError):
#     data: JSONLikeObject = {d
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

# @dataclass
# class UpstreamJSONRPCErrorData(JSONLikeObject):
#     status_code: int
#     code: int
#     message: str
#     data: Optional[JSONLike] = None


class UpstreamJSONRPCError(ServiceErrorX):
    def __init__(self, message: str, data: JSONRPCError):
        error_data = jsonable_encoder(data)
        super().__init__(
            ERRORS.upstream_jsonrpc_error.code,
            ERRORS.upstream_jsonrpc_error.title,
            message,
            data=error_data,
            status_code=502,
        )


class UpstreamError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(
            ERRORS.upstream_error.code,
            ERRORS.upstream_error.title,
            message,
            status_code=502,
        )


# Used when boxed in by the type system.
class ImpossibleError(ServiceErrorX):
    def __init__(self, message: str):
        super().__init__(1099, "Impossible Error", message, status_code=500)
