from pydantic import Field

from orcidlink.jsonrpc.errors import ERRORS_MAP, ErrorDescription, NotFoundError
from orcidlink.lib.type import ServiceBaseModel


class ErrorInfoParams(ServiceBaseModel):
    error_code: int = Field(...)


class ErrorInfoResult(ServiceBaseModel):
    error_info: ErrorDescription


def error_info_method(error_code: int) -> ErrorInfoResult:
    error = ERRORS_MAP.get(error_code)

    if error is None:
        raise NotFoundError("Error info not found")

    return ErrorInfoResult(error_info=error)
