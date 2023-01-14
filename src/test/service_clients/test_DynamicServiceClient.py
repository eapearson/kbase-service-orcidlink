import contextlib
import time

import pytest
from orcidlink.service_clients.DynamicServiceClient import DynamicServiceClient
from orcidlink.service_clients.error import SERVER_ERROR_MIN
from test.mocks.mock_contexts import (
    mock_imaginary_service,
    mock_service_wizard_service,
    no_stderr,
)
from test.mocks.mock_server import MockServer
from test.mocks.mock_service_wizard_service import MockServiceWizardService


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_service_wizard_service() as [_, _, url]:
            yield url


def test_DynamicServiceClient_constructor():
    # happy paths.
    client = DynamicServiceClient(url="foo", module="bar", timeout=1)
    client._initialize_cache(force=True)

    assert client is not None

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(url="foo", module="bar")

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(url="foo")

    with pytest.raises(TypeError) as te:
        DynamicServiceClient()

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(url="foo", timeout=1)

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(module="bar", timeout=1)

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(timeout=1)

    with pytest.raises(TypeError) as te:
        DynamicServiceClient(module="bar")


def test_DynamicServiceClient_lookup_url():
    with mock_services() as url:
        client = DynamicServiceClient(
            url=url, timeout=1, module="ORCIDLink", version="dev", token=None
        )
        client._initialize_cache(force=True)

        result = client._lookup_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"

        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is False
        result = client._get_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is True

        result = client._get_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is True

        client.clear_cache()
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is False

        # result = client._lookup_url("ORCIDLink", None)
        # assert result is not None
        # assert result.get("module_name") == "ORCIDLink"


def test_DynamicServiceClient_lookup_url_with_ttl():
    with mock_services() as url:
        client = DynamicServiceClient(
            url=url,
            timeout=1,
            module="ORCIDLink",
            version="dev",
            token=None,
            cache_ttl=1,
        )
        client._initialize_cache(force=True)

        result = client._lookup_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"

        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is False
        result = client._get_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is True

        result = client._get_url(1)
        assert result is not None
        assert result == "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink"
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is True

        # client.clear_cache()
        time.sleep(2)
        assert DynamicServiceClient._cache().has_key("ORCIDLink:dev") is False

        # result = client._lookup_url("ORCIDLink", None)
        # assert result is not None
        # assert result.get("module_name") == "ORCIDLink"


def test_DynamicServiceClient_call_func():
    with no_stderr():
        with mock_imaginary_service() as [_, mock_imaginary_service_class, url]:

            class MockServiceWizardService2(MockServiceWizardService):
                def send_service_status(
                    self, method: str, module_name: str, version: str | None
                ):
                    if module_name == "ImaginaryService":
                        if version == "dev" or version is None:
                            self.increment_method_call_count(method, "success")
                            self.send_json(
                                self.success_response(
                                    {
                                        "git_commit_hash": "HASH",
                                        "status": "active",
                                        "hash": "HASH",
                                        "release_tags": ["dev"],
                                        "url": url,
                                        "module_name": "ImaginaryService",
                                        "health": "healthy",
                                        "up": 1,
                                    }
                                )
                            )
                        else:
                            self.increment_method_call_count(method, "error")
                            self.send_json(
                                self.error_response(
                                    SERVER_ERROR_MIN,
                                    "Server error",
                                    message="'No module version found that matches your criteria!'",
                                )
                            )
                    else:
                        self.increment_method_call_count(method, "error")
                        self.send_json(
                            self.error_response(
                                SERVER_ERROR_MIN,
                                "Server error",
                                message="'Module cannot be found based on module_name or git_url parameters.'",
                            )
                        )

            service_wizard_server = MockServer("127.0.0.1", MockServiceWizardService2)
            try:
                MockServiceWizardService.reset_call_counts()
                service_wizard_server.start_service()
                mock_imaginary_service_class.reset_call_counts()

                client = DynamicServiceClient(
                    url=f"{service_wizard_server.base_url()}/services/service_wizard/rpc",
                    timeout=1,
                    module="ImaginaryService",
                    version="dev",
                    token=None,
                )

                result = client.call_func("status")
                assert result is not None
            except Exception as ex:
                pytest.fail(f"Exception raised when not expected: {str(ex)}")
            finally:
                service_wizard_server.stop_service()
