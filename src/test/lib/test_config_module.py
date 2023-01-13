import pytest
from orcidlink.lib import config
from orcidlink.service_clients.DynamicServiceClient import DynamicServiceClient
from test.data.utils import load_data_file
from test.mocks.mock_contexts import mock_service_wizard_service, no_stderr

config_yaml = load_data_file('config1.yaml')

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
    config.ensure_config(reload=True)
    assert config.config().module.CLIENT_ID == 'REDACTED-CLIENT-ID'
    assert config.config().module.CLIENT_SECRET == 'REDACTED-CLIENT-SECRET'
    assert config.config().module.IS_DYNAMIC_SERVICE == 'no'
    assert config.config().kbase.services.Auth2.url == 'https://ci.kbase.us/services/auth/api/V2/token'


# def test_get_config_not_found(my_config_file):
#     config.ensure_config(reload=True)
#     with pytest.raises(ValueError):
#         config.get_config(['foo'])


def test_get_service_url_from_config(my_config_file2):
    config.ensure_config(reload=True)
    assert config.get_service_url() == 'https://ci.kbase.us/services/ORCIDLink'


def test_get_service_path_from_config(my_config_file2):
    config.ensure_config(reload=True)
    assert config.get_service_path() == '/services/ORCIDLink'


def test_get_service_info(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            config.clear()
            config.ensure_config(reload=True)

            # modify the service wizard url to use the dynamically allocated
            # server address.
            config.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()

            assert mock_class.total_call_count['success'] == 0

            service_info = config.get_service_info()
            assert service_info is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_info = config.get_service_info()
            assert service_info is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_get_service_url(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            config.clear()
            config.ensure_config(reload=True)

            # hack the service wizard url to use the dynamically allocated
            # server address. Could probably do this with a different usage of
            # the my_config_file fixture.
            config.ensure_config()
            config.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()
            assert mock_class.total_call_count['success'] == 0

            service_url = config.get_service_url()
            assert service_url is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['error'] == 0
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_url = config.get_service_url()
            assert service_url is not None
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_get_service_path(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [server, mock_class, _]:
            mock_class.reset_call_counts()
            config.clear()
            config.ensure_config(reload=True)

            # hack the service wizard url to use the dynamically allocated
            # server address. Could probably do this with a different usage of
            # the my_config_file fixture.
            config.ensure_config()
            config.config().kbase.services.ServiceWizard.url = f"{server.base_url()}/services/service_wizard/rpc"

            # reset dynamic service client cache.
            DynamicServiceClient.clear_cache()
            assert mock_class.total_call_count['success'] == 0

            service_path = config.get_service_path()
            assert service_path is not None
            # see my_config_file
            assert service_path == "/dynserv/HASH.ORCIDLink"
            # assert method was called successfully.
            assert mock_class.total_call_count['error'] == 0
            assert mock_class.total_call_count['success'] == 1

            # If we call again, the service wizard should not be called.
            service_path = config.get_service_path()
            assert service_path is not None
            assert service_path == "/dynserv/HASH.ORCIDLink"
            # assert method was called successfully.
            assert mock_class.total_call_count['success'] == 1


def test_set_config(my_config_file):
    with no_stderr():
        with mock_service_wizard_service() as [_, mock_class, _]:
            mock_class.reset_call_counts()

            # modify the service wizard url to use the dynamically allocated
            # server address.
            config.ensure_config()

            config.clear()
            config.ensure_config(reload=True)

            # Set to different value, should be changed.
            config.config().kbase.services.ServiceWizard.url = "FOO"
            assert config.config().kbase.services.ServiceWizard.url == "FOO"

            # Set to same value, nothing should change
            config.config().kbase.services.ServiceWizard.url = "FOO"
            assert config.config().kbase.services.ServiceWizard.url == "FOO"

            # with pytest.raises(ValueError, match="Config not found on path: kbase.services.ServiceWizard.url2") as ex:
            #     config.set_config(["kbase", "services", "ServiceWizard", "url2"], "FOO")
