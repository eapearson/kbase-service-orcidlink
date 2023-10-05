#
# Runtime support
#

import os

from orcidlink.lib.config import RuntimeConfig, ServiceConfig
from orcidlink.lib.utils import posix_time_millis

CONFIG: RuntimeConfig | None = None


class RuntimeStats:
    start_time: int

    def __init__(self) -> None:
        self.start_time = posix_time_millis()


STATS: RuntimeStats | None = None


def config() -> RuntimeConfig:
    global CONFIG
    if CONFIG is None:
        CONFIG = ServiceConfig().runtime_config
    return CONFIG


def stats() -> RuntimeStats:
    global STATS
    if STATS is None:
        STATS = RuntimeStats()
    return STATS


def service_path(path: str) -> str:
    return os.path.join(config().service_directory, path)
