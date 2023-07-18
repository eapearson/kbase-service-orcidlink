from __future__ import annotations

import os
from datetime import datetime, timezone


def module_dir() -> str:
    my_dir = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(my_dir, "../../.."))


def module_path(path: str) -> str:
    return os.path.join(module_dir(), path)


def posix_time_millis() -> int:
    """
    Returns the current epoch, or UTC, time in milliseconds

    This function is handy to capture this pattern, as we prefer to
    return time in milliseconds for all KBase apis.
    """
    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)


def make_date(
    year: int | None = None, month: int | None = None, day: int | None = None
) -> str:
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
