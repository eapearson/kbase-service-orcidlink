import os
import re
from typing import List

import yaml
from lib.ServiceWizard import ServiceWizard
from lib.utils import get_prop, module_dir

CONFIG = None


def ensure_config():
    global CONFIG
    if CONFIG is not None:
        return CONFIG

    file_name = os.path.join(module_dir(), "config/config.yaml")
    with open(file_name, "r") as in_file:
        return yaml.load(in_file, yaml.SafeLoader)


def get_config(key_path: List[str], default_value=None):
    config = ensure_config()
    value = get_prop(config, key_path, default_value)
    if value is None:
        raise ValueError(f"Config not found on path: {'.'.join(key_path)}")
    return value


def get_service_uri():
    # TODO: cache this.
    if get_config(["env", "IS_DYNAMIC_SERVICE"]) == "yes":
        service_wizard = ServiceWizard(get_config(["kbase", "services", "ServiceWizard", "url"]), None)
        service_info, error = service_wizard.get_service_status('ORCIDLink', None)
        base_url = re.sub(r"https://(.*?)(?:[:][\d]*)?/", r"https://\1/", service_info['url'])
        return base_url
    else:
        return get_config(["kbase", "services", "ORCIDLink", "url"])


def get_service_path():
    # TODO: cache this.
    if get_config(["env", "IS_DYNAMIC_SERVICE"]) == "yes":
        service_wizard = ServiceWizard(get_config(["kbase", "services", "ServiceWizard", "url"]), None)
        service_info, error = service_wizard.get_service_status('ORCIDLink', None)

        match = re.match(r"^https://(.*?)(/.*)$", service_info["url"])

        if match is None:
            raise ValueError('Cannot parse the dynamic service url');

        return match.group(2)
    else:
        # TODO
        return get_config(["kbase", "services", "ORCIDLink", "url"])
