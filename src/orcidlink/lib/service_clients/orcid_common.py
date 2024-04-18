#
# Errors
#

from typing import Any, Optional

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel


class ORCIDStringValue(ServiceBaseModel):
    value: str = Field(...)


#
# This is the usual error response for 500; I don't remember how this was
# triggered!
#
class APIResponseInternalServerError(ServiceBaseModel):
    message_version: str = Field(
        validation_alias="message-version", serialization_alias="message-version"
    )
    orcid_profile: Optional[Any] = Field(
        default=None,
        validation_alias="orcid-profile",
        serialization_alias="orcid-profile",
    )
    orcid_search_results: Optional[Any] = Field(
        default=None,
        validation_alias="orcid-search-results",
        serialization_alias="orcid-search-results",
    )
    error_desc: ORCIDStringValue = Field(
        validation_alias="error-desc", serialization_alias="error-desc"
    )


# This is return for at least 401
class APIResponseUnauthorized(ServiceBaseModel):
    error: str = Field(...)
    error_description: Optional[str] = Field(
        default=None,
        validation_alias="error-description",
        serialization_alias="error-description",
    )


#
# INVESTIGATE
#


class APIResponseUnknownError(ServiceBaseModel):
    detail: Any = Field(...)


class APIParseError(ServiceBaseModel):
    error_text: str = Field(
        validation_alias="error-text", serialization_alias="error-text"
    )
