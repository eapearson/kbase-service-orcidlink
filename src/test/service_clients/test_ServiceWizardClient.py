import contextlib

import pytest
from orcidlink.service_clients.ServiceWizard import ServiceWizard
from orcidlink.service_clients.error import SERVER_ERROR_MIN, ServiceError
from test.mocks.mock_contexts import mock_service_wizard_service, no_stderr


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_service_wizard_service() as [server, _, _]:
            yield f"{server.base_url()}/services/service_wizard/rpc"


def test_get_service_status():
    with mock_services() as url:
        client = ServiceWizard(url=url, timeout=1, token=None)
        result = client.get_service_status("ORCIDLink", "dev")
        assert result is not None
        assert result.get("module_name") == "ORCIDLink"

        result = client.get_service_status("ORCIDLink", None)
        assert result is not None
        assert result.get("module_name") == "ORCIDLink"


def test_call_func_version_does_not_match():
    with mock_services() as url:
        client = ServiceWizard(url=url, timeout=1, token=None)
        with pytest.raises(ServiceError) as ex:
            client.get_service_status("ORCIDLink", "beta")

        assert ex.value.code == SERVER_ERROR_MIN
        assert (
            ex.value.message == "'No module version found that matches your criteria!'"
        )


def test_call_func_invalid_version():
    with mock_services() as url:
        client = ServiceWizard(url=url, timeout=1, token=None)
        with pytest.raises(
            TypeError,
            match="module version must be one of 'dev', 'beta', 'release', or None",
        ) as ex:
            client.get_service_status("ORCIDLink", "foo")


def test_constructor_errors():
    with pytest.raises(TypeError, match='The "url" named argument is required') as ex:
        ServiceWizard()

    with pytest.raises(
        TypeError, match='The "timeout" named argument is required'
    ) as ex:
        ServiceWizard(url=f"http:/foo/services/service_wizard/rpc")

    with pytest.raises(TypeError, match='The "url" named argument is required') as ex:
        ServiceWizard(timeout=1)


def test_status():
    with mock_services() as url:
        client = ServiceWizard(url=url, timeout=1, token=None)
        result = client.status()
        assert result is not None
        assert result.get("state") == "OK"
