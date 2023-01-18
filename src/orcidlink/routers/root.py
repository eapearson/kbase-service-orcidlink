from fastapi import APIRouter
from orcidlink.lib.config import Config, config, get_kbase_config
from orcidlink.lib.utils import epoch_time_millis
from orcidlink.model import KBaseSDKConfig
from pydantic import BaseModel, Field

router = APIRouter(prefix="/link", responses={404: {"description": "Not found"}})

from fastapi import APIRouter

router = APIRouter(prefix="", responses={404: {"description": "Not found"}})


# TODO: move into config!!
# STARTED = epoch_time_millis()


class StatusResponse(BaseModel):
    status: str = Field(...)
    time: int = Field(...)
    start_time: int = Field(...)


@router.get("/status", response_model=StatusResponse, tags=["misc"])
async def get_status():
    """
    The status of the service.

    The intention of this endpoint is as a lightweight way to call to ping the
    service, e.g. for health check, latency tests, etc.
    """
    # TODO: start time, deal with it@
    return StatusResponse(status="ok", start_time=0, time=epoch_time_millis())


class InfoResponse(BaseModel):
    kbase_sdk_config: KBaseSDKConfig = Field(...)
    config: Config = Field(...)


@router.get("/info", response_model=InfoResponse, tags=["misc"])
async def get_info():
    """
    Returns basic information about the service and its runtime configuration.
    """
    # TODO: version should either be separate call, or derived from the a file stamped during the build.
    kbase_sdk_config = get_kbase_config()
    config_copy = config().dict()
    config_copy["orcid"]["clientId"] = "REDACTED"
    config_copy["orcid"]["clientSecret"] = "REDACTED"
    config_copy["mongo"]["username"] = "REDACTED"
    config_copy["mongo"]["password"] = "REDACTED"
    return {"kbase_sdk_config": kbase_sdk_config, "config": config_copy}


# Docs
