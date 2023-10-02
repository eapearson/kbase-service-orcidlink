import logging

from pydantic import Field

from orcidlink.lib.config import GitInfo, get_git_info, get_service_description
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.model import ServiceDescription


class InfoResult(ServiceBaseModel):
    service_description: ServiceDescription = Field(alias="service-description")
    git_info: GitInfo = Field(alias="git-info")


def info_method() -> InfoResult:
    service_description = get_service_description()
    git_info = get_git_info()

    logger = logging.getLogger("api")
    logger.info(
        "Successfully called /info method",
        extra={"type": "api", "params": None, "path": "/info"},
    )

    return InfoResult.model_validate(
        {
            "service-description": service_description,
            "git-info": git_info,
        }
    )
