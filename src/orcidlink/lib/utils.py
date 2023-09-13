from datetime import datetime, timezone


def posix_time_millis() -> int:
    """
    Returns the current epoch, or UTC, time in milliseconds

    This function is handy to capture this pattern, as we prefer to
    return time in milliseconds for all KBase apis.
    """
    return int(datetime.now(tz=timezone.utc).timestamp() * 1000)


def posix_time_seconds() -> int:
    """
    Returns the current epoch, or UTC, time in milliseconds

    This function is handy to capture this pattern, as we prefer to
    return time in milliseconds for all KBase apis.
    """
    return int(datetime.now(tz=timezone.utc).timestamp())


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
