import contextlib
import json
from typing import AnyStr
from orcidlink.lib.type import ServiceBaseModel
from test.mocks.data import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.responses import JSONResponse, RedirectResponse, Response

from orcidlink.lib.utils import module_path
from orcidlink.lib.responses import (
    success_response_no_data,
    error_response,
    exception_error_response,
    exception_error_response,
    ui_error_response,
)
from orcidlink.lib.responses import error_response_not_found
import os
from unittest import mock

# config_yaml = load_data_file("config1.toml")
MOCK_KBASE_SERVICES_PORT = 9999
MOCK_ORCID_API_PORT = 9997
MOCK_ORCID_OAUTH_PORT = 9997

TEST_ENV = {
    "KBASE_ENDPOINT": f"http://127.0.0.1:{MOCK_KBASE_SERVICES_PORT}/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "MONGO_HOST": "mongo",
    "MONGO_PORT": "27017",
    "MONGO_DATABASE": "orcidlink",
    "MONGO_USERNAME": "dev",
    "MONGO_PASSWORD": "d3v",
    "ORCID_API_BASE_URL": f"http://127.0.0.1:{MOCK_ORCID_API_PORT}",
    "ORCID_OAUTH_BASE_URL": f"http://127.0.0.1:{MOCK_ORCID_OAUTH_PORT}",
}


# @contextlib.contextmanager
# def mock_services():
#     with no_stderr():
#         with mock_auth_service():
#             yield


@pytest.fixture
def fake_fs(fs):
    # fs.create_file(f"{utils.module_dir()}/deploy/config.toml", contents=config_yaml)
    fs.add_real_directory(module_path("test/data"))
    yield fs


def test_success_response_no_data():
    value = success_response_no_data()
    assert isinstance(value, Response)
    assert value.status_code == 204


def test_error_response():
    class TestData(ServiceBaseModel):
        some: str

    value = error_response(
        "codex", "title", "message", data=TestData(some="data"), status_code=123
    )
    assert isinstance(value, JSONResponse)
    assert value.status_code == 123
    # The JSONResponse structure is not in scope for this project; it is simply provided to
    # fastapi which utilizes it for the response
    assert value.body is not None


def test_exception_error_response():
    try:
        raise Exception("I am exceptional")
    except Exception as ex:
        value = exception_error_response("codex", "title", ex, status_code=123)
        assert isinstance(value, JSONResponse)
        assert value.status_code == 123
        # The JSONResponse structure is not in scope for this project; it is simply provided to
        # fastapi which utilizes it for the response.
        # Still, the whole point of testing this is to assure ourselves that the response is as we expect,
        # so ... here we go.
        assert value.body is not None
        data = json.loads(value.body)
        assert data["code"] == "codex"
        assert data["title"] == "title"
        assert data["message"] == "I am exceptional"
        assert isinstance(data["data"]["traceback"], list)


def test_exception_error_response_no_data():
    try:
        raise Exception("I am exceptional")
    except Exception as ex:
        value = exception_error_response("codex", "title", ex, status_code=123)
        assert isinstance(value, JSONResponse)
        assert value.status_code == 123
        # The JSONResponse structure is not in scope for this project; it is simply provided to
        # fastapi which utilizes it for the response.
        # Still, the whole point of testing this is to assure ourselves that the response is as we expect,
        # so ... here we go.
        assert value.body is not None
        data = json.loads(value.body)
        assert data["code"] == "codex"
        assert data["title"] == "title"
        assert data["message"] == "I am exceptional"
        assert data["data"]["exception"] == "I am exceptional"
        assert isinstance(data["data"]["traceback"], list)


def as_str(something: str | bytes) -> str:
    if isinstance(something, str):
        return something
    else:
        return str(something, encoding="utf-8")


def test_ui_error_response(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        value = ui_error_response("codex", "title", "message")
        assert isinstance(value, RedirectResponse)
        assert value.status_code == 302
        assert "location" in value.headers
        location_value = value.headers.get("location")
        assert location_value is not None
        assert location_value.endswith("#orcidlink/error")
        url = urlparse(value.headers.get("location"))
        assert url.scheme == "http"
        assert url.path == ""
        assert url.hostname == "127.0.0.1"
        assert url.fragment == "orcidlink/error"
        # assert url.query
        # annoyingly, may be string or bytes, so coerce, primarily to make
        # typing happy.
        query_string = as_str(url.query)
        query = parse_qs(query_string)  # type: ignore
        assert "code" in query
        assert query["code"] == ["codex"]

        # assert data["code"] == "code"
        # assert data["title"] == "title"
        # assert data["message"] == "message"


def test_error_response_not_found():
    value = error_response_not_found("Foo not found")

    assert isinstance(value, JSONResponse)
    assert value.status_code == 404
    # the response body is bytes, which we can convert
    # back to a dict...
    body_json = json.loads(value.body)
    assert isinstance(body_json, dict)
    assert body_json["code"] == "notFound"
    assert body_json["title"] == "Not Found"
    assert body_json["message"] == "Foo not found"
