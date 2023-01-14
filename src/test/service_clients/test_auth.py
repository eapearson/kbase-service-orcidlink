import pytest
from orcidlink.service_clients import auth
from test.data.utils import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr

config_yaml = load_data_file("config1.yaml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_auth_get_username(fake_fs):
    with no_stderr():
        with mock_auth_service():
            assert auth.get_username("foo") == "foo"
