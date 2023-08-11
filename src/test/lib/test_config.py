import os
from unittest import mock

import pytest

from orcidlink.lib.config import Config2, IntConstantDefault

TEST_ENV = {
    "KBASE_ENDPOINT": f"http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "FOO": "123",
}


def test_get_config():
    """
    Test all config properties with default behavior, if available.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        config = Config2()
        assert config.get_auth_url() == "http://foo/services/auth"
        assert config.get_workspace_url() == "http://foo/services/ws"
        assert config.get_cache_lifetime() == 300
        assert config.get_cache_max_items() == 20000
        assert config.get_request_timeout() == 60
        assert config.get_ui_origin() == "http://foo"
        assert Config2.get_int_constant(
            IntConstantDefault(value=123, required=True, env_name="FOO")
        )


TEST_ENV_BAD = {
    "NO_KBASE_ENDPOINT": f"http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "FOO": "123",
}


def test_get_config_bad_env():
    with mock.patch.dict(os.environ, TEST_ENV_BAD, clear=True):
        with pytest.raises(
            ValueError, match='The "KBASE_ENDPOINT" environment variable was not found'
        ):
            Config2()
