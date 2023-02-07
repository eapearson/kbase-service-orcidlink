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
import threading
from typing import Optional

import toml
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import module_dir
from orcidlink.model import ServiceDescription
from pydantic import Field


class KBaseService(ServiceBaseModel):
    url: str = Field(...)


class Auth2Service(KBaseService):
    tokenCacheLifetime: int = Field(...)
    tokenCacheMaxSize: int = Field(...)


class ORCIDLinkService(KBaseService):
    pass


class ORCIDConfig(ServiceBaseModel):
    oauthBaseURL: str = Field(...)
    apiBaseURL: str = Field(...)
    clientId: str = Field(...)
    clientSecret: str = Field(...)


class MongoConfig(ServiceBaseModel):
    host: str = Field(...)
    port: int = Field(...)
    database: str = Field(...)
    username: str = Field(...)
    password: str = Field(...)


class ModuleConfig(ServiceBaseModel):
    serviceRequestTimeout: int = Field(...)


class Services(ServiceBaseModel):
    Auth2: Auth2Service
    ORCIDLink: ORCIDLinkService = Field(...)


class UIConfig(ServiceBaseModel):
    origin: str = Field(...)


class Config(ServiceBaseModel):
    services: Services = Field(...)
    ui: UIConfig = Field(...)
    orcid: ORCIDConfig = Field(...)
    mongo: MongoConfig = Field(...)
    module: ModuleConfig = Field(...)


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


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.lock = threading.RLock()
        self.config_data = self.get_config_data()

    def get_config_data(self) -> Config:
        with self.lock:
            file_name = self.config_path
            with open(file_name, "r") as in_file:
                config_yaml = toml.load(in_file)
                return Config.parse_obj(config_yaml)

    def config(self, reload: bool = False) -> Config:
        if reload:
            self.config_data = self.get_config_data()

        return self.config_data


GLOBAL_CONFIG_MANAGER = None


def config(reload: bool = False) -> Config:
    global GLOBAL_CONFIG_MANAGER
    if GLOBAL_CONFIG_MANAGER is None:
        GLOBAL_CONFIG_MANAGER = ConfigManager(
            os.path.join(module_dir(), "deploy/config.toml")
        )
    return GLOBAL_CONFIG_MANAGER.config(reload)


def get_service_description() -> ServiceDescription:
    file_path = os.path.join(module_dir(), "SERVICE_DESCRIPTION.toml")
    with open(file_path, "r") as file:
        return ServiceDescription.parse_obj(toml.load(file))


def get_git_info() -> GitInfo:
    path = os.path.join(module_dir(), "deploy/git-info.toml")
    with open(path, "r") as fin:
        return GitInfo.parse_obj(toml.load(fin))
