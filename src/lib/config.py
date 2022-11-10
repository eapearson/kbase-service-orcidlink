import json
import os
import re

from lib.ServiceWizard import ServiceWizard
from lib.utils import get_prop, module_dir

CONFIG = None


def get_config(key_path, default_value=None):
    global CONFIG
    if CONFIG is None:
        file_name = os.path.join(module_dir(), "config/config.json")
        with open(file_name, "r") as in_file:
            CONFIG = json.load(in_file)
    value = get_prop(CONFIG, key_path, default_value)
    if value == None:
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
