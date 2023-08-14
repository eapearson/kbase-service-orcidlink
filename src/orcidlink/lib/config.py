"""
Configuration support for this service

A KBase service requires at least a minimal, and often substantial, configuration in order to operate.
Some configuration, like the base url for services, differs between each KBase environment.
Other configuration represents information that may change over time, such as urls.
Sill other configuration data contains private information like credentials, which must be well controlled.

Because configuration is needed throughout the service's code, it is provided by means of a module variable
which is populated when the module is first loaded.
"""
import os
from typing import Optional
from urllib.parse import urljoin, urlparse

from pydantic import Field
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.model import ServiceDescription
from orcidlink.lib.utils import module_dir
import toml


class GitInfo(ServiceBaseModel):
    commit_hash: str = Field(...)
    commit_hash_abbreviated: str = Field(...)
    author_name: str = Field(...)
    author_date: int = Field(...)
    committer_name: str = Field(...)
    committer_date: int = Field(...)
    url: str = Field(...)
    branch: str = Field(...)
    tag: Optional[str] = Field(default=None)


class ServiceDefault(ServiceBaseModel):
    path: str = Field(...)
    env_name: str = Field(...)


class ServiceDefaults(ServiceBaseModel):
    auth2: ServiceDefault = Field(...)
    workspace: ServiceDefault = Field(...)
    orcid_link: ServiceDefault = Field(...)


SERVICE_DEFAULTS = ServiceDefaults(
    auth2=ServiceDefault(path="auth", env_name="KBASE_SERVICE_AUTH"),
    workspace=ServiceDefault(path="ws", env_name="KBASE_SERVICE_WORKSPACE"),
    orcid_link=ServiceDefault(path="orcidlink", env_name="KBASE_SERVICE_ORCID_LINK"),
)


class IntConstantDefault(ServiceBaseModel):
    value: Optional[int] = Field(default=None)
    required: bool = Field(...)
    env_name: str = Field(...)


class IntConstantDefaults(ServiceBaseModel):
    token_cache_lifetime: IntConstantDefault = Field(...)
    token_cache_max_items: IntConstantDefault = Field(...)
    request_timeout: IntConstantDefault = Field(...)
    mongo_port: IntConstantDefault = Field(...)


INT_CONSTANT_DEFAULTS = IntConstantDefaults(
    token_cache_lifetime=IntConstantDefault(
        value=300, required=True, env_name="TOKEN_CACHE_LIFETIME"
    ),
    token_cache_max_items=IntConstantDefault(
        value=20000, required=True, env_name="TOKEN_CACHE_MAX_ITEMS"
    ),
    request_timeout=IntConstantDefault(
        value=60, required=True, env_name="REQUEST_TIMEOUT"
    ),
    mongo_port=IntConstantDefault(required=True, env_name="MONGO_PORT"),
)


# String constants


class StrConstantDefault(ServiceBaseModel):
    value: Optional[str] = Field(default=None)
    required: bool = Field(...)
    env_name: str = Field(...)


class StrConstantDefaults(ServiceBaseModel):
    kbase_endpoint: StrConstantDefault = Field(...)
    orcid_api_base_url: StrConstantDefault = Field(...)
    orcid_oauth_base_url: StrConstantDefault = Field(...)
    orcid_client_id: StrConstantDefault = Field(...)
    orcid_client_secret: StrConstantDefault = Field(...)
    mongo_host: StrConstantDefault = Field(...)
    mongo_database: StrConstantDefault = Field(...)
    mongo_username: StrConstantDefault = Field(...)
    mongo_password: StrConstantDefault = Field(...)


STR_CONSTANT_DEFAULTS = StrConstantDefaults(
    kbase_endpoint=StrConstantDefault(required=True, env_name="KBASE_ENDPOINT"),
    orcid_api_base_url=StrConstantDefault(required=True, env_name="ORCID_API_BASE_URL"),
    orcid_oauth_base_url=StrConstantDefault(
        required=True, env_name="ORCID_OAUTH_BASE_URL"
    ),
    orcid_client_id=StrConstantDefault(required=True, env_name="ORCID_CLIENT_ID"),
    orcid_client_secret=StrConstantDefault(
        required=True, env_name="ORCID_CLIENT_SECRET"
    ),
    mongo_host=StrConstantDefault(required=True, env_name="MONGO_HOST"),
    mongo_database=StrConstantDefault(required=True, env_name="MONGO_DATABASE"),
    mongo_username=StrConstantDefault(required=True, env_name="MONGO_USERNAME"),
    mongo_password=StrConstantDefault(required=True, env_name="MONGO_PASSWORD"),
)


class RuntimeConfig(ServiceBaseModel):
    kbase_endpoint: str = Field(...)
    request_timeout: int = Field(...)
    token_cache_lifetime: int = Field(...)
    token_cache_max_items: int = Field(...)
    orcid_api_base_url: str = Field(...)
    orcid_oauth_base_url: str = Field(...)
    orcid_client_id: str = Field(...)
    orcid_client_secret: str = Field(...)
    mongo_host: str = Field(...)
    mongo_port: int = Field(...)
    mongo_database: str = Field(...)
    mongo_username: str = Field(...)
    mongo_password: str = Field(...)

    ui_origin: str = Field(...)

    workspace_url: str = Field(...)
    auth_url: str = Field(...)
    orcidlink_url: str = Field(...)


class Config2:
    kbase_endpoint: str
    runtime_config: RuntimeConfig

    def __init__(self) -> None:
        self.kbase_endpoint = self.get_str_constant(
            STR_CONSTANT_DEFAULTS.kbase_endpoint
        )
        self.runtime_config = RuntimeConfig(
            kbase_endpoint=self.get_str_constant(STR_CONSTANT_DEFAULTS.kbase_endpoint),
            request_timeout=self.get_int_constant(
                INT_CONSTANT_DEFAULTS.request_timeout
            ),
            token_cache_lifetime=self.get_int_constant(
                INT_CONSTANT_DEFAULTS.token_cache_lifetime
            ),
            token_cache_max_items=self.get_int_constant(
                INT_CONSTANT_DEFAULTS.token_cache_max_items
            ),
            orcid_api_base_url=self.get_str_constant(
                STR_CONSTANT_DEFAULTS.orcid_api_base_url
            ),
            orcid_oauth_base_url=self.get_str_constant(
                STR_CONSTANT_DEFAULTS.orcid_oauth_base_url
            ),
            orcid_client_id=self.get_str_constant(
                STR_CONSTANT_DEFAULTS.orcid_client_id
            ),
            orcid_client_secret=self.get_str_constant(
                STR_CONSTANT_DEFAULTS.orcid_client_secret
            ),
            mongo_host=self.get_str_constant(STR_CONSTANT_DEFAULTS.mongo_host),
            mongo_port=self.get_int_constant(INT_CONSTANT_DEFAULTS.mongo_port),
            mongo_database=self.get_str_constant(STR_CONSTANT_DEFAULTS.mongo_database),
            mongo_username=self.get_str_constant(STR_CONSTANT_DEFAULTS.mongo_username),
            mongo_password=self.get_str_constant(STR_CONSTANT_DEFAULTS.mongo_password),
            ui_origin=self.get_ui_origin(),
            auth_url=self.get_service_url(SERVICE_DEFAULTS.auth2),
            workspace_url=self.get_service_url(SERVICE_DEFAULTS.workspace),
            orcidlink_url=self.get_service_url(SERVICE_DEFAULTS.orcid_link),
        )

    def get_service_url(self, service_default: ServiceDefault) -> str:
        env_path = os.environ.get(service_default.env_name)
        path = env_path or service_default.path
        return urljoin(self.kbase_endpoint, path)

    # MORE...

    # Integer constants

    @staticmethod
    def get_int_constant(constant_default: IntConstantDefault) -> int:
        value = os.environ.get(constant_default.env_name)

        if value is not None:
            return int(value)

        if constant_default.value is not None:
            return constant_default.value

        raise ValueError(
            f'The environment variable "{constant_default.env_name}" is missing and there is no default value'
        )

    # String constants
    @staticmethod
    def get_str_constant(constant_default: StrConstantDefault) -> str:
        value = os.environ.get(constant_default.env_name)

        if value is not None:
            return value

        if constant_default.value is not None:
            return constant_default.value

        raise ValueError(
            f'The environment variable "{constant_default.env_name}" is missing and there is no default value'
        )

    # misc

    def get_ui_origin(self) -> str:
        endpoint_url = urlparse(self.kbase_endpoint)
        # [protocol, _, endpoint_host] = self.kbase_endpoint.split('/')[2]
        host = (
            "narrative.kbase.us"
            if endpoint_url.hostname == "kbase.us"
            else endpoint_url.netloc
        )
        return f"{endpoint_url.scheme}://{endpoint_url.hostname}"


def get_service_description() -> ServiceDescription:
    file_path = os.path.join(module_dir(), "SERVICE_DESCRIPTION.toml")
    with open(file_path, "r", encoding="utf-8") as file:
        return ServiceDescription.model_validate(toml.load(file))


def get_git_info() -> GitInfo:
    path = os.path.join(module_dir(), "build/git-info.toml")
    with open(path, "r", encoding="utf-8") as fin:
        return GitInfo.model_validate(toml.load(fin))
