from __future__ import annotations

import os
import time
from datetime import datetime, timezone


def module_dir() -> str:
    my_dir = os.path.dirname(__file__)
    return os.path.realpath(os.path.join(my_dir, "../../.."))


def current_time_millis() -> int:
    return int(round(time.time() * 1000))


def epoch_time_millis() -> int:
    epoch_time = datetime.now(tz=timezone.utc).timestamp()
    return int(epoch_time * 1000)


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
