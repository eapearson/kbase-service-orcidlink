# This is one form of error message returned by ORCID API
from enum import Enum
from typing import Optional

from pydantic import Field

from orcidlink.lib.type import ServiceBaseModel


class ORCIDAPIError(ServiceBaseModel):
    """
    One form of error response from the ORCID API.
    """

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


#
# The OAuth Bearer error has the same basic shape as the basic OAuth error,
# but the range of error codes (see the enum below) is different.
#


class OAUthBearerErrorEnum(str, Enum):
    # for bearer tokens
    invalid_request = "invalid_request"
    invalid_token = "invalid_token"
    insufficient_scope = "insufficient_scope"


#  SEE https://www.rfc-editor.org/rfc/rfc6750
class OAuthBearerError(ServiceBaseModel):
    """
    Although the name implies it is only for OAuth API errors, it may also be returned
    for authentication-related errors via the ORCID API.

    See https://datatracker.ietf.org/doc/html/rfc6749#page-45
    """

    error: OAUthBearerErrorEnum = Field(...)
    error_description: Optional[str] = Field(default=None)
    error_uri: Optional[str] = Field(default=None)


#
# The general OAuth error, as may be encountered during OAuth flow
#


class OAUthErrorEnum(str, Enum):
    invalid_request = "invalid_request"
    invalid_client = "invalid_client"
    invalid_grant = "invalid_grant"
    unauthorized_client = "unauthorized_client"
    unsupported_grant_type = "unsupported_grant_type"
    invalid_scope = "invalid_scope"


class OAuthError(ServiceBaseModel):
    """
    Although the name implies it is only for OAuth API errors, it may also be returned
    for authentication-related errors via the ORCID API.

    See https://datatracker.ietf.org/doc/html/rfc6749#page-45
    """

    error: OAUthErrorEnum = Field(...)
    error_description: Optional[str] = Field(default=None)
    error_uri: Optional[str] = Field(default=None)
