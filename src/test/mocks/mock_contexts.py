import contextlib
import os
from test.mocks.mock_auth import MockAuthService
from test.mocks.mock_imaginary_service import MockImaginaryService
from test.mocks.mock_orcid import (
    MockORCIDAPI,
    MockORCIDAPIWithErrors,
    MockORCIDOAuth,
    MockORCIDOAuth2,
)
from test.mocks.mock_server import MockSDKJSON11Service, MockServer


@contextlib.contextmanager
def no_stderr():
    with contextlib.redirect_stderr(open(os.devnull, "w", encoding="utf-8")):
        yield


@contextlib.contextmanager
def mock_auth_service(port: int):
    service = MockServer("127.0.0.1", port, MockAuthService)
    try:
        service.start_service()
        url = f"{service.base_url()}/services/auth/api/V2/token"
        yield [service, MockAuthService, url, port]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_oauth_service(port: int):
    service = MockServer("127.0.0.1", port, MockORCIDOAuth)
    try:
        service.start_service()
        url = service.base_url()
        yield [service, MockORCIDOAuth, url, port]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_oauth_service2(port: int):
    service = MockServer("127.0.0.1", port, MockORCIDOAuth2)
    try:
        service.start_service()
        url = service.base_url()
        yield [service, MockORCIDOAuth2, url, port]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_api_service(port: int):
    service = MockServer("127.0.0.1", port, MockORCIDAPI)
    try:
        service.start_service()
        url = service.base_url()
        yield [service, MockORCIDAPI, url, port]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_api_service_with_errors(port: int):
    service = MockServer("127.0.0.1", port, MockORCIDAPIWithErrors)
    try:
        service.start_service()
        url = service.base_url()
        yield [service, MockORCIDAPIWithErrors, url, port]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_imaginary_service(port: int):
    server = MockServer("127.0.0.1", port, MockImaginaryService)
    MockImaginaryService.reset_call_counts()
    try:
        server.start_service()
        url = f"{server.base_url()}/services/imaginary_service"
        yield [server, MockImaginaryService, url, port]
    finally:
        server.stop_service()


@contextlib.contextmanager
def mock_jsonrpc11_service(port: int):
    server = MockServer("127.0.0.1", port, MockSDKJSON11Service)
    MockSDKJSON11Service.reset_call_counts()
    try:
        server.start_service()
        url = f"{server.base_url()}/services/my_service"
        yield [server, MockSDKJSON11Service, url, port]
    finally:
        server.stop_service()
