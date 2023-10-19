from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.runtime import stats


class StatusResult(ServiceBaseModel):
    status: str = Field(...)
    current_time: int = Field(...)
    start_time: int = Field(...)


def status_method() -> StatusResult:
    return StatusResult(
        status="ok", start_time=stats().start_time, current_time=posix_time_millis()
    )
