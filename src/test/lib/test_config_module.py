import pytest
from orcidlink.lib import config
from test.data.utils import load_data_file

config_yaml = load_data_file("config1.toml")
config_yaml2 = load_data_file("config2.toml")


@pytest.fixture
def my_config_file(fs):
    fs.create_file("/kb/module/deploy/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


@pytest.fixture
def my_config_file2(fs):
    fs.create_file("/kb/module/deploy/config.toml", contents=config_yaml2)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_get_config(my_config_file2):
    # Force reload of the mock config to a pristine state.
    config.config(reload=True)
    assert config.config().orcid.clientId == "REDACTED-CLIENT-ID"
    assert config.config().orcid.clientSecret == "REDACTED-CLIENT-SECRET"
    assert (
        config.config().services.Auth2.url
        == "https://ci.kbase.us/services/auth/api/V2/token"
    )


def test_config_initially_none(my_config_file2):
    """
    Various
    It is difficult to test this in the natural state, in which the
    global config manager in the config module starts life as None, but
    is initialized upon first usage. That lifecycle depends upon the
    application lifecycle, and with tests we don't
    have control over that. So we simulate that by resetting it to None first.
    """
    # Force reload of the mock config to a pristine state.
    config.GLOBAL_CONFIG_MANAGER = None
    assert config.GLOBAL_CONFIG_MANAGER is None
    config.config()
    assert config.GLOBAL_CONFIG_MANAGER is not None
    assert config.config().ui.origin == "https://ci.kbase.us"


def test_set_config(my_config_file):
    config.config()

    config.config().services.ORCIDLink.url = "BAR"
    assert config.config().services.ORCIDLink.url == "BAR"

    # Set to different value, should be changed.
    config.config().services.ORCIDLink.url = "FOO"
    assert config.config().services.ORCIDLink.url == "FOO"

    # Set to same value, nothing should change
    config.config().services.ORCIDLink.url = "FOO"
    assert config.config().services.ORCIDLink.url == "FOO"
