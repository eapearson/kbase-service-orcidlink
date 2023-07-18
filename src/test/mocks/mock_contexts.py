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

from orcidlink.lib import config


@contextlib.contextmanager
def no_stderr():
    with contextlib.redirect_stderr(open(os.devnull, "w", encoding="utf-8")):
        yield


@contextlib.contextmanager
def mock_auth_service():
    service = MockServer("127.0.0.1", MockAuthService)
    try:
        service.start_service()
        url = f"{service.base_url()}/services/auth/api/V2/token"
        config.config().services.Auth2.url = url

        yield [service, MockAuthService, url]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_oauth_service():
    service = MockServer("127.0.0.1", MockORCIDOAuth)
    try:
        service.start_service()
        url = service.base_url()
        config.config().orcid.oauthBaseURL = url
        yield [service, MockORCIDOAuth, url]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_oauth_service2():
    service = MockServer("127.0.0.1", MockORCIDOAuth2)
    try:
        service.start_service()
        url = service.base_url()
        config.config().orcid.oauthBaseURL = url
        yield [service, MockORCIDOAuth2, url]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_api_service():
    service = MockServer("127.0.0.1", MockORCIDAPI)
    try:
        service.start_service()
        url = service.base_url()
        config.config().orcid.apiBaseURL = url
        yield [service, MockORCIDAPI, url]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_orcid_api_service_with_errors():
    service = MockServer("127.0.0.1", MockORCIDAPIWithErrors)
    try:
        service.start_service()
        url = service.base_url()
        config.config().orcid.apiBaseURL = url
        yield [service, MockORCIDAPIWithErrors, url]
    finally:
        service.stop_service()


@contextlib.contextmanager
def mock_imaginary_service():
    server = MockServer("127.0.0.1", MockImaginaryService)
    MockImaginaryService.reset_call_counts()
    try:
        server.start_service()
        url = f"{server.base_url()}/services/imaginary_service"
        yield [server, MockImaginaryService, url]
    finally:
        server.stop_service()


@contextlib.contextmanager
def mock_jsonrpc11_service():
    server = MockServer("127.0.0.1", MockSDKJSON11Service)
    MockSDKJSON11Service.reset_call_counts()
    try:
        server.start_service()
        url = f"{server.base_url()}/services/my_service"
        yield [server, MockSDKJSON11Service, url]
    finally:
        server.stop_service()
