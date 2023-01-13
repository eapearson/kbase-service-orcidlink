import os

import pytest
from orcidlink.lib import config
from orcidlink.lib.utils import module_dir
from orcidlink.service_clients.DynamicServiceClient import DynamicServiceClient
from test.data.utils import load_data_file
from test.mocks.mock_contexts import mock_service_wizard_service, no_stderr

config_yaml = load_data_file('config1.yaml')
config_yaml2 = load_data_file('config2.yaml')


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
    assert c.config().module.CLIENT_ID == 'REDACTED-CLIENT-ID'
    assert c.config().module.CLIENT_SECRET == 'REDACTED-CLIENT-SECRET'
    assert c.config().module.IS_DYNAMIC_SERVICE == 'no'
    assert c.config().kbase.services.Auth2.url == 'https://ci.kbase.us/services/auth/api/V2/token'


# def test_get_config_not_found(my_config_file):
#     config = Config(os.path.join(module_dir(), "config/config.yaml"))
#     with pytest.raises(ValueError):
#         config.get_config(['foo'])


def test_get_service_url_from_config(my_config_file2):
    cm = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))
    assert cm.get_service_url() == 'https://ci.kbase.us/services/ORCIDLink'


def test_get_service_path_from_config(my_config_file2):
    cm = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))
    assert cm.get_service_path() == '/services/ORCIDLink'


def test_get_service_info(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            # This is the config instance we are going to test
            cm = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))

            mock_class.reset_call_counts()

            # Modfy the service wizard url to use the dynamically allocated
            # server address.
            cm.ensure_config()
            cm.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()

            assert mock_class.total_call_count['success'] == 0

            service_info = cm.get_service_info()
            assert service_info is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_info = cm.get_service_info()
            assert service_info is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_get_service_url(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            cm = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))

            # hack the service wizard url to use the dynamically allocated
            # server address. Could probably do this with a different usage of
            # the my_config_file fixture.
            cm.ensure_config()
            cm.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            mock_class.reset_call_counts()

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()

            assert mock_class.total_call_count['success'] == 0

            service_url = cm.get_service_url()
            assert service_url is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['error'] == 0
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_url = cm.get_service_url()
            assert service_url is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_get_service_path(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            cm = config.ConfigManager(os.path.join(module_dir(), "config/config.yaml"))

            # hack the service wizard url to use the dynamically allocated
            # server address. Could probably do this with a different usage of
            # the my_config_file fixture.
            cm.ensure_config()
            cm.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            mock_class.reset_call_counts()

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()

            assert mock_class.total_call_count['success'] == 0

            service_path = cm.get_service_path()
            assert service_path is not None
            # see my_config_file
            assert service_path == "/dynserv/HASH.ORCIDLink"
            # assert method was called successfully.
            assert mock_class.total_call_count['error'] == 0
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_path = cm.get_service_path()
            assert service_path is not None
            assert service_path == "/dynserv/HASH.ORCIDLink"
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_get_kbase_config():
    value = config.get_kbase_config()
    assert value is not None
    assert value.get('module-name') == 'ORCIDLink'
    assert value.get('service-language') == 'python'
    assert isinstance(value.get("module-description"), str)
    assert isinstance(value.get("module-version"), str)
    assert value.get('service-config').get('dynamic-service') is True
