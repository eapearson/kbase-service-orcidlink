#
# Configuration
#

from orcidlink.lib.config import Config2, RuntimeConfig

CONFIG: RuntimeConfig | None = None


def config() -> RuntimeConfig:
    global CONFIG
    if CONFIG is None:
        CONFIG = Config2().runtime_config
    return CONFIG
