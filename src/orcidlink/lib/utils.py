import os
import time
from typing import List

import yaml


def module_dir():
    my_dir = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(my_dir, "../../.."))


def get_prop(value, path: List[str | int]):
    for name in path:
        if isinstance(value, dict):
            value = value.get(name)
            if value is None:
                return None, False
        elif isinstance(value, list):
            if isinstance(name, int):
                if name >= len(value) or name < 0:
                    return None, False
                value = value[name]
            else:
                return None, False
    return value, True


def set_prop(value, path: List[str | int], new_value):
    temp = value
    *head, tail = path
    for name in head:
        if isinstance(temp, dict):
            if name not in temp:
                raise ValueError(f"Cannot set prop; cannot get path element '{name}' in dict")
            temp = temp.get(name)
        elif isinstance(temp, list):
            if isinstance(name, int):
                if name >= len(temp) or name < 0:
                    raise ValueError(f"Cannot set prop; cannot get path element '{name}' in array")
                temp = temp[name]
            else:
                raise ValueError(f"Cannot set prop; path element '{name}' is not int for array")
        else:
            raise ValueError("Cannot set prop; reached leaf too early")

    # should be on a leaf node. what is it?
    if isinstance(temp, dict):
        if tail not in temp:
            raise ValueError(f"Cannot set prop; cannot get leaf element '{tail}' in dict")
        temp[tail] = new_value
    elif isinstance(temp, list):
        if isinstance(tail, int):
            if tail >= len(temp) or tail < 0:
                raise ValueError(f"Cannot set prop; cannot get leaf element '{tail}' in array")
            temp[tail] = new_value
        else:
            raise ValueError(f"Cannot set prop; leaf path element '{tail}' is not int for array")
    else:
        raise ValueError("Cannot set prop; leaf is not a dict or list")


def get_raw_prop(value, path: List[str | int], default_value=None):
    found_value, found = get_prop(value, path)
    if found:
        return found_value
    return default_value


def get_string_prop(value, path: List[str | int], default_value=None):
    found_value, found = get_prop(value, path)
    if found:
        return str(found_value)
    return default_value


def get_int_prop(value, path: List[str | int], default_value=None):
    found_value, found = get_prop(value, path)
    if found:
        return int(found_value)
    return default_value


def current_time_millis():
    return int(round(time.time() * 1000))


def make_date(year: int | None = None, month: int | None = None, day: int | None = None):
    if year is not None:
        if month is not None:
            if day is not None:
                return f"{year}/{month}/{day}"
            else:
                return f"{year}/{month}"
        else:
            return f"{year}"
    else:
        return "** invalid date **"


def get_kbase_config():
    config_path = os.path.join(module_dir(), './kbase.yml')
    with open(config_path, "r") as kbase_config_file:
        return yaml.load(kbase_config_file, yaml.SafeLoader)
