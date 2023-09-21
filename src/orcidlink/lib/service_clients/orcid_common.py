#
# Errors
#

from typing import Any, Optional

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel


class ORCIDStringValue(ServiceBaseModel):
    value: str = Field(...)


# This is the usual error response for 4xx
class APIResponseError(ServiceBaseModel):
    response_code: int = Field(
        validation_alias="response-code", serialization_alias="response-code"
    )
    developer_message: str = Field(
        validation_alias="developer-message", serialization_alias="developer-message"
    )
    user_message: str = Field(
        validation_alias="user-message", serialization_alias="user-message"
    )
    error_code: int = Field(
        validation_alias="error-code", serialization_alias="error-code"
    )
    more_info: str = Field(
        validation_alias="more-info", serialization_alias="more-info"
    )


# This is the usual error response for 500
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


# Please list here cases in which this is returned:
# /ORCID/record with bad token
# /ORCID/record with revoked trusted party access


class ORCIDAPIError(ServiceBaseModel):
    error: str = Field(...)
    error_description: str = Field(...)


class APIResponseUnknownError(ServiceBaseModel):
    detail: Any = Field(...)


class APIParseError(ServiceBaseModel):
    error_text: str = Field(
        validation_alias="error-text", serialization_alias="error-text"
    )
