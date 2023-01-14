import os
import threading

import yaml
from orcidlink.lib.utils import module_dir
from orcidlink.service_clients.ServiceWizard import ServiceWizard
from pydantic import BaseModel, Field


class KBaseService(BaseModel):
    url: str = Field(...)


class Auth2Service(KBaseService):
    tokenCacheLifetime: int = Field(...)
    tokenCacheMaxSize: int = Field(...)


class ORCIDLinkService(KBaseService):
    pass


class ServiceWizardService(KBaseService):
    pass


class ORCIDConfig(BaseModel):
    oauthBaseURL: str = Field(...)
    baseURL: str = Field(...)
    apiBaseURL: str = Field(...)


class ModuleConfig(BaseModel):
    CLIENT_ID: str = Field(...)
    CLIENT_SECRET: str = Field(...)
    IS_DYNAMIC_SERVICE: str = Field(...)
    MONGO_USERNAME: str = Field(...)
    MONGO_PASSWORD: str = Field(...)
    STORAGE_MODEL: str = Field(...)


class Services(BaseModel):
    Auth2: Auth2Service
    ServiceWizard: ServiceWizardService
    ORCIDLink: ORCIDLinkService = Field(...)


class Defaults(BaseModel):
    serviceRequestTimeout: int = Field(...)


class KBaseConfig(BaseModel):
    services: Services
    uiOrigin: str = Field(...)
    defaults: Defaults


class Config(BaseModel):
    kbase: KBaseConfig
    orcid: ORCIDConfig
    module: ModuleConfig


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.service_info = None
        self.lock = threading.RLock()
        # self.config_data: Optional[Config] = None
        self.config_data = self.get_config_data()

    def get_config_data(self) -> Config:
        with self.lock:
            file_name = self.config_path
            with open(file_name, "r") as in_file:
                config_yaml = yaml.load(in_file, yaml.SafeLoader)
                return Config.parse_obj(config_yaml)

    def config(self, reload: bool = False) -> Config:
        if reload:
            self.config_data = self.get_config_data()

        return self.config_data

    def ensure_config(self, reload: bool = False) -> Config:
        return self.config(reload)

    def get_service_info(self):
        # TODO: cache this.
        if self.service_info is None:
            service_wizard = ServiceWizard(
                url=self.config_data.kbase.services.ServiceWizard.url,
                token=None,
                timeout=self.config_data.kbase.defaults.serviceRequestTimeout / 1000,
            )
            self.service_info = service_wizard.get_service_status("ORCIDLink", None)

        return self.service_info

    def clear(self):
        with self.lock:
            self.service_info = None
            self.config_data = None

    # def get_service_url(self) -> str:
    #     self.config()
    #     if self.config_data.module.IS_DYNAMIC_SERVICE == "yes":
    #         return re.sub(r"https://(.*?)(?::\d*)?/", r"https://\1/", self.get_service_info()['url'])
    #     return self.config_data.kbase.services.ORCIDLink.url
    #
    # def get_service_path(self) -> str:
    #     match = re.match(r"^https://(.*?)(/.*)$", self.get_service_url())
    #     # we assume that the service provides correct responses!
    #
    #     return match.group(2)


GLOBAL_CONFIG = ConfigManager(os.path.join(module_dir(), "config/config.yaml"))


# CONFIG = None
# lock = threading.RLock()


def ensure_config(reload: bool = False):
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.ensure_config(reload)


def config(reload: bool = False) -> Config:
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.config(reload)


#
# # TODO: add a lock around t.his.
# SERVICE_INFO = None
#
#
def get_service_info():
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.get_service_info()


def clear():
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.clear()


def get_service_url():
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.get_service_url()


def get_service_path():
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.get_service_path()


def get_kbase_config():
    config_path = os.path.join(module_dir(), "./kbase.yml")
    with open(config_path, "r") as kbase_config_file:
        return yaml.load(kbase_config_file, yaml.SafeLoader)
