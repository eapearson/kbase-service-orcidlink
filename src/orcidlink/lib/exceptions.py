from typing import Any, Dict, Optional

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import Field

from orcidlink.lib.errors import ERRORS, ErrorCode2
from orcidlink.lib.json_file import JSONLikeObject
from orcidlink.lib.service_clients.jsonrpc import JSONRPCError
from orcidlink.lib.type import ServiceBaseModel


class ServiceErrorY(Exception):
    error: ErrorCode2
    message: str

    def __init__(
        self, error: ErrorCode2, message: str, data: Optional[ServiceBaseModel] = None
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


class AlreadyLinkedError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.already_linked, message)


class AuthorizationRequiredError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.authorization_required, message)


class UnauthorizedError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.not_authorized, message)


class NotFoundError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.not_found, message)


class InternalServerError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.internal_server_error, message)


class JSONDecodeErrorData(ServiceBaseModel):
    message: str


class JSONDecodeError(ServiceErrorY):
    def __init__(self, message: str, data: JSONDecodeErrorData):
        # data = JSONDecodeErrorData(decodeErrorMessage=str(jde))
        super().__init__(ERRORS.json_decode_error, message, data=data)


class ContentTypeErrorData(ServiceBaseModel):
    originalContentType: Optional[str] = Field(default=None)


class ContentTypeError(ServiceErrorY):
    data: ContentTypeErrorData

    def __init__(self, message: str, data: ContentTypeErrorData):
        # data = ContentTypeErrorData()

        # if cte.headers is not None:
        #     data.originalContentType = cte.headers["content-type"]

        super().__init__(ERRORS.content_type_error, message, data=data)


class UpstreamErrorData(ServiceBaseModel):
    status_code: int
    source: str
    detail: Optional[Dict[str, Any]] = Field(default=None)
    message: Optional[str] = Field(default=None)


class UpstreamORCIDAPIError(ServiceErrorY):
    data: UpstreamErrorData

    def __init__(self, message: str, data: UpstreamErrorData):
        super().__init__(ERRORS.upstream_orcid_error, message, data)


class UpstreamJSONRPCError(ServiceErrorY):
    def __init__(self, message: str, data: JSONRPCError):
        error_data = jsonable_encoder(data)
        super().__init__(ERRORS.upstream_jsonrpc_error, message, data=error_data)


class UpstreamError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.upstream_error, message)


# ORCID Errors
class ORCIDProfileNamePrivate(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.orcid_profile_name_private, message)


# Used when boxed in by the type system.
class ImpossibleError(ServiceErrorY):
    def __init__(self, message: str):
        super().__init__(ERRORS.impossible_error, message)
