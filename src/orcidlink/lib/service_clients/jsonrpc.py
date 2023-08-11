import os
from typing import Any

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel


class JSONRPCError(ServiceBaseModel):
    code: int = Field(...)
    message: str = Field(...)
    data: Any | None = Field(default=None)
