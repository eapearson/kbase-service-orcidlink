import os
from unittest import mock

import pytest

from orcidlink.lib.config import (
    Config2,
    IntConstantDefault,
    StrConstantDefault,
    get_git_info,
    get_service_description,
)
from orcidlink.lib.utils import module_path
from test.mocks.data import load_data_file


service_description_toml = load_data_file("service_description1.toml")
git_info_toml = load_data_file("git_info1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file(
        module_path("SERVICE_DESCRIPTION.toml"), contents=service_description_toml
    )
    fs.create_file(module_path("build/git-info.toml"), contents=git_info_toml)
    fs.add_real_directory(module_path("test/data"))
    yield fs


TEST_ENV = {
    "KBASE_ENDPOINT": "http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "ORCID_API_BASE_URL": "http://orcidapi",
    "ORCID_OAUTH_BASE_URL": "http://orcidoauth",
    "ORCID_CLIENT_ID": "CLIENT-ID",
    "ORCID_CLIENT_SECRET": "CLIENT-SECRET",
    "MONGO_HOST": "MONGO-HOST",
    "MONGO_PORT": "1234",
    "MONGO_DATABASE": "MONGO-DATABASE",
    "MONGO_USERNAME": "MONGO-USERNAME",
    "MONGO_PASSWORD": "MONGO-PASSWORD",
    # "TOKEN_CACHE_LIFETIME": "60",
    # "TOKEN_CACHE_MAX_ITEMS": "10",
    # "REQUEST_TIMEOUT": "60",
    "FOO": "123",
}


def test_get_config():
    """
    Test all config properties with default behavior, if available.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        config = Config2().runtime_config
        assert config.auth_url == "http://foo/services/auth"
        assert config.workspace_url == "http://foo/services/ws"
        assert config.orcidlink_url == "http://foo/services/orcidlink"
        assert config.token_cache_lifetime == 300
        assert config.token_cache_max_items == 20000
        assert config.request_timeout == 60
        assert config.ui_origin == "http://foo"
        assert config.orcid_api_base_url == "http://orcidapi"
        assert config.orcid_oauth_base_url == "http://orcidoauth"
        assert config.orcid_client_id == "CLIENT-ID"
        assert config.orcid_client_secret == "CLIENT-SECRET"
        assert config.mongo_host == "MONGO-HOST"
        assert config.mongo_port == 1234
        assert config.mongo_database == "MONGO-DATABASE"
        assert config.mongo_username == "MONGO-USERNAME"
        assert config.mongo_password == "MONGO-PASSWORD"


TEST_ENV_BAD = {
    "NO_KBASE_ENDPOINT": f"http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "FOO": "123",
}


def test_get_config_bad_env():
    with mock.patch.dict(os.environ, TEST_ENV_BAD, clear=True):
        with pytest.raises(
            ValueError,
            match='The environment variable "KBASE_ENDPOINT" is missing and there is no default value',
        ):
            Config2()


# get_int_constant


def test_get_int_constant_no_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_int_constant(
            IntConstantDefault(required=True, env_name="FOO")
        )
        assert value == 123


def test_get_int_constant_with_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_int_constant(
            IntConstantDefault(required=True, env_name="FOO", value=456)
        )
        assert value == 123


def test_get_int_constant_missing_with_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_int_constant(
            IntConstantDefault(required=True, env_name="BAR", value=100)
        )
        assert value == 100


def test_get_int_constant_missing_no_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with pytest.raises(
            ValueError,
            match='The environment variable "BAR" is missing and there is no default value',
        ):
            Config2.get_int_constant(IntConstantDefault(required=True, env_name="BAR"))


# get_str_constant


def test_get_str_constant_no_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_str_constant(
            StrConstantDefault(required=True, env_name="FOO")
        )
        assert value == "123"


def test_get_str_constant_with_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_str_constant(
            StrConstantDefault(required=True, env_name="FOO", value="456")
        )
        assert value == "123"


def test_get_str_constant_missing_with_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = Config2.get_str_constant(
            StrConstantDefault(required=True, env_name="BAR", value="baz")
        )
        assert value == "baz"


def test_get_str_constant_missing_no_default():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with pytest.raises(
            ValueError,
            match='The environment variable "BAR" is missing and there is no default value',
        ):
            Config2.get_str_constant(StrConstantDefault(required=True, env_name="BAR"))


def test_get_service_description(fake_fs):
    service_description = get_service_description()
    assert service_description is not None
    assert service_description.version == "1.2.3"
    assert service_description.name == "ORCIDLink"


def test_git_info(fake_fs):
    git_info = get_git_info()
    assert git_info.commit_hash_abbreviated == "678c42c"
    assert git_info.author_name == "Foo Bar"
