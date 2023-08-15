#
# Runtime support
#

from orcidlink.lib.config import Config2, RuntimeConfig
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
        CONFIG = Config2().runtime_config
    return CONFIG


def stats() -> RuntimeStats:
    global STATS
    if STATS is None:
        STATS = RuntimeStats()
    return STATS
