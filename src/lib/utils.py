import os
import time


def module_dir():
    my_dir = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(my_dir, "../.."))


def get_prop(value, path, default_value=None):
    temp = value
    for name in path:
        if isinstance(temp, dict):
            temp = temp.get(name)
            if temp is None:
                return default_value
        elif isinstance(temp, list):
            # Why doesn't pop mirror the behavior of get?
            if isinstance(name, int):
                if name >= len(temp) or name < 0:
                    return default_value
                    # raise ValueError(f"List index out of range: {name} in path {path}")
                temp = temp[name]
            else:
                return default_value
                # raise ValueError(
                #     f"Path element for list node must be int: {type(name)}"
                # )
    return temp


def get_int_prop(value, path, default_value=None):
    temp = value
    for name in path:
        if isinstance(temp, dict):
            temp = temp.get(name)
            if temp is None:
                return default_value
        elif isinstance(temp, list):
            if isinstance(name, int):
                if name >= len(temp) or name < 0:
                    return default_value
                temp = temp[name]
            else:
                return default_value
    return int(temp)


def current_time_millis():
    return int(round(time.time() * 1000))


def make_date(year, month, day):
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
    return os.path.join(module_dir(), './kbase.yml')
