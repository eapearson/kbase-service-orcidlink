import logging

from fastapi import APIRouter, Path
from pydantic import Field

from orcidlink.lib.config import GitInfo, get_git_info, get_service_description
from orcidlink.lib.errors import ERRORS, ERRORS_MAP, ErrorCode2
from orcidlink.lib.exceptions import ServiceErrorY
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import ServiceDescription
from orcidlink.runtime import stats

router = APIRouter(prefix="")


class StatusResponse(ServiceBaseModel):
    status: str = Field(...)
    current_time: int = Field(...)
    start_time: int = Field(...)


@router.get(
    "/status",
    response_model=StatusResponse,
    tags=["misc"],
    responses={
        200: {
            "description": "Successfully returns the service status",
            "model": StatusResponse,
        }
    },
)
async def get_status() -> StatusResponse:
    """
    Get Service Status

    This endpoint returns the current status of the service. The status code itself
    is always "ok", by definition. Other information includes the current time, and the
    start time.

    It can be used as a healthcheck, for basic latency measurement (as it makes no
    i/o or other high-latency calls), or for time synchronization (as it returns the
    current time).
    """

    logger = logging.getLogger("api")
    logger.info(
        "Successfully called /info method",
        extra={"type": "api", "params": None, "path": "/status"},
    )

    return StatusResponse(
        status="ok", start_time=stats().start_time, current_time=posix_time_millis()
    )


class InfoResponse(ServiceBaseModel):
    service_description: ServiceDescription = Field(alias="service-description")
    git_info: GitInfo = Field(alias="git-info")


@router.get("/info", response_model=InfoResponse, tags=["misc"])
async def get_info() -> InfoResponse:
    """
    Get Service Information

    Returns basic information about the service and its configuration.
    """
    # TODO: version should either be separate call, or derived from the a
    # file stamped during the build.
    service_description = get_service_description()
    git_info = get_git_info()

    logger = logging.getLogger("api")
    logger.info(
        "Successfully called /info method",
        extra={"type": "api", "params": None, "path": "/info"},
    )

    return InfoResponse.model_validate(
        {
            "service-description": service_description,
            "git-info": git_info,
        }
    )


# ERROR_CODE_PARAM = Annotated[int, Path(
#     description="The orcid id", regex="^[\\d]{4}$"
#     # It is a uuid, whose string representation is 36 characters.
# )]


ERROR_CODE_PARAM = Path(
    description="The orcid id"
    # It is a uuid, whose string representation is 36 characters.
)


class ErrorInfoResponse(ServiceBaseModel):
    error_info: ErrorCode2


@router.get("/error-info/{error_code}", response_model=ErrorInfoResponse, tags=["misc"])
async def get_error_info(error_code: int = ERROR_CODE_PARAM) -> ErrorInfoResponse:
    """
    Returns information about a given error.

    Useful for presenting standardized error information in interfaces.
    """
    # Find the error code
    # error = [error for error in ERRORS]
    error = ERRORS_MAP.get(error_code)

    if error is None:
        raise ServiceErrorY(error=ERRORS.not_found, message="Error info not found")

    return ErrorInfoResponse(error_info=error)
