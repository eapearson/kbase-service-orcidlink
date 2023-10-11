import logging

from pydantic import Field

from orcidlink.lib.config import GitInfo, get_git_info, get_service_description
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import ServiceDescription
from orcidlink.runtime import config


class RuntimeInfo(ServiceBaseModel):
    """
    Information about the current runtime environment that may be useful or necessary
    for a user of this service.
    """

    current_time: int = Field(...)
    orcid_api_url: str = Field(...)
    orcid_oauth_url: str = Field(...)
    orcid_site_url: str = Field(...)


class InfoResult(ServiceBaseModel):
    service_description: ServiceDescription = Field(
        validation_alias="service-description",
        serialization_alias="service-description",
    )
    git_info: GitInfo = Field(
        validation_alias="git-info", serialization_alias="git-info"
    )
    runtime_info: RuntimeInfo = Field(...)


def info_method() -> InfoResult:
    service_description = get_service_description()
    git_info = get_git_info()

    logger = logging.getLogger("api")
    logger.info(
        "Successfully called /info method",
        extra={"type": "api", "params": None, "path": "/info"},
    )

    runtime_info = RuntimeInfo(
        current_time=posix_time_millis(),
        orcid_api_url=config().orcid_api_base_url,
        orcid_oauth_url=config().orcid_oauth_base_url,
        orcid_site_url=config().orcid_site_base_url,
    )

    return InfoResult(
        service_description=service_description,
        git_info=git_info,
        runtime_info=runtime_info,
    )
