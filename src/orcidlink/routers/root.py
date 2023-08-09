import json

from fastapi import APIRouter
from pydantic import Field
from orcidlink.lib.config import GitInfo, get_git_info, get_service_description

from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import ServiceDescription

router = APIRouter(prefix="")


class StatusResponse(ServiceBaseModel):
    status: str = Field(...)
    time: int = Field(...)
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

    With no parameters, this endpoint returns the current status of the service. The status code itself
    is always "ok". Other information includes the current time, and the start time.

    It can be used as a healthcheck, for basic latency performance (as it makes no
    i/o or other high-latency calls), or for time synchronization (as it returns the current time).
    """
    # TODO: start time, deal with it@
    return StatusResponse(status="ok", start_time=0, time=posix_time_millis())


class InfoResponse(ServiceBaseModel):
    service_description: ServiceDescription = Field(alias="service-description")
    git_info: GitInfo = Field(alias="git-info")


@router.get("/info", response_model=InfoResponse, tags=["misc"])
async def get_info() -> InfoResponse:
    """
    Get Service Information

    Returns basic information about the service and its runtime configuration.
    """
    # TODO: version should either be separate call, or derived from the a
    # file stamped during the build.
    service_description = get_service_description()
    git_info = get_git_info()

    # NB we can mix dict and model here.
    return InfoResponse.model_validate(
        {
            "service-description": service_description,
            "git-info": git_info,
        }
    )
