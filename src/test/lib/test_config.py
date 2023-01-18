import os

import pytest
from orcidlink.lib import config
from orcidlink.lib.utils import module_dir
from test.data.utils import load_data_file

config_yaml = load_data_file("config1.yaml")
config_yaml2 = load_data_file("config2.yaml")


@pytest.fixture
def my_config_file(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


@pytest.fixture
def my_config_file2(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml2)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_get_config(my_config_file2):
    c = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))
    assert c.config().orcid.clientId == "REDACTED-CLIENT-ID"
    assert c.config().orcid.clientSecret == "REDACTED-CLIENT-SECRET"
    assert (
        c.config().kbase.services.Auth2.url
        == "https://ci.kbase.us/services/auth/api/V2/token"
    )


def test_get_kbase_config():
    value = config.get_kbase_config()
    assert value is not None
    assert value.get("module-name") == "ORCIDLink"
    assert value.get("service-language") == "python"
    assert isinstance(value.get("module-description"), str)
    assert isinstance(value.get("module-version"), str)
    assert value.get("service-config").get("dynamic-service") is False
