from typing import Any

from pydantic import BaseModel, Field

from src.model_types import KBaseSDKConfig

# class CustomBaseModel(BaseModel):
#     def dict(self, **kwargs):
#         redacted_fields = set(
#             attribute_name
#             for attribute_name, model_field in self.__fields__.items()
#             if model_field.field_info.extra.get("redact") is True
#         )
#         kwargs.setdefault("")


#
# API Typing
#
class StatusResponse(BaseModel):
    status: str = Field(...)
    time: str = Field(...)


class ServiceConfig(BaseModel):
    url: str = Field(...)


class Auth2Config(ServiceConfig):
    tokenCacheLifetime: int = Field(...)
    tokenCacheMaxSize: int = Field(...)


class ServicesConfig(BaseModel):
    Auth2: Auth2Config = Field(...)
    ServiceWizard: ServiceConfig = Field(...)


class KBaseConfig(BaseModel):
    services: ServicesConfig = Field(...)
    # services: Any
    uiOrigin: str = Field(...)


class ORCIDConfig(BaseModel):
    oauthBaseURL: str = Field(...)
    tokenExchangeURL: str = Field(...)
    tokenRevokeURL: str = Field(...)
    baseURL: str = Field(...)
    apiBaseURL: str = Field(...)
    authorizeURL: str = Field(...)


class EnvConfig(BaseModel):
    CLIENT_ID: str = Field(...)
    CLIENT_SECRET: str = Field(...)
    IS_DYNAMIC_SERVICE: str = Field(...)


class Config(BaseModel):
    kbase: KBaseConfig = Field(...)
    orcid: ORCIDConfig = Field(...)
    env: EnvConfig = Field(...)


class InfoResponse(BaseModel):
    kbase_sdk_config: KBaseSDKConfig = Field(...)
    config: Config = Field(...)


class GetIsLinkedResult(BaseModel):
    result: bool = Field(...)
