import os
import re
import threading
from typing import Any, List

import yaml
from orcidlink.lib.utils import get_prop, module_dir, set_prop
from orcidlink.service_clients.ServiceWizard import ServiceWizard


class Config:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.service_info = None
        self.lock = threading.RLock()

    def ensure_config(self, reload: bool = False):
        if self.config is None or reload:
            with self.lock:
                file_name = self.config_path
                with open(file_name, "r") as in_file:
                    self.config = yaml.load(in_file, yaml.SafeLoader)

        return self.config

    def get_config(self, key_path: List[str], reload: bool = False):
        config = self.ensure_config(reload=reload)
        value, found = get_prop(config, key_path)
        if not found:
            raise ValueError(f"Config not found on path: {'.'.join(key_path)}")
        return value

    def set_config(self, key_path: List[str], new_value: Any, reload: bool = False):
        config = self.ensure_config(reload=reload)
        existing_value, found = get_prop(config, key_path)
        if not found:
            raise ValueError(f"Config not found on path: {'.'.join(key_path)}")

        if existing_value == new_value:
            return

        set_prop(config, key_path, new_value)
        return

    def get_service_info(self):
        # TODO: cache this.
        if self.service_info is None:
            service_wizard = ServiceWizard(
                url=self.get_config(["kbase", "services", "ServiceWizard", "url"]),
                token=None,
                timeout=self.get_config(["kbase", "defaults", "serviceRequestTimeout"]) / 1000
            )
            self.service_info = service_wizard.get_service_status('ORCIDLink', None)

        return self.service_info

    def clear(self):
        with self.lock:
            self.service_info = None
            self.config = None

    def get_service_url(self):
        if self.get_config(["env", "IS_DYNAMIC_SERVICE"]) == "yes":
            return re.sub(r"https://(.*?)(?::\d*)?/", r"https://\1/", self.get_service_info()['url'])
        return self.get_config(["kbase", "services", "ORCIDLink", "url"])

    def get_service_path(self):
        match = re.match(r"^https://(.*?)(/.*)$", self.get_service_url())
        # we assume that the service provides correct responses!
        return match.group(2)


GLOBAL_CONFIG = Config(os.path.join(module_dir(), "config/config.yaml"))


# CONFIG = None
# lock = threading.RLock()


def ensure_config(reload: bool = False):
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.ensure_config(reload)


def get_config(key_path: List[str], reload: bool = False):
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.get_config(key_path, reload=reload)


def set_config(key_path: List[str], new_value: Any, reload: bool = False):
    global GLOBAL_CONFIG
    return GLOBAL_CONFIG.set_config(key_path, new_value, reload=reload)


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
