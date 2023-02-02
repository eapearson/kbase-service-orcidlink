import contextlib
import json
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib import responses
from orcidlink.lib.responses import error_response_not_found
from test.data.utils import load_data_file
from test.mocks.mock_contexts import mock_auth_service, no_stderr

config_yaml = load_data_file("config1.toml")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            yield


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/deploy/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_success_response_no_data():
    value = responses.success_response_no_data()
    assert isinstance(value, Response)
    assert value.status_code == 204


def test_error_response():
    value = responses.error_response(
        "codex", "title", "message", data={"some": "data"}, status_code=123
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
        value = responses.exception_error_response(
            "codex", "title", ex, status_code=123
        )
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
        value = responses.exception_error_response(
            "codex", "title", ex, status_code=123
        )
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


def test_ui_error_response(fake_fs):
    value = responses.ui_error_response("codex", "title", "message")
    assert isinstance(value, RedirectResponse)
    assert value.status_code == 302
    assert "location" in value.headers
    assert value.headers.get("location").endswith("#orcidlink/error")
    url = urlparse(value.headers.get("location"))
    assert url.scheme == "https"
    assert url.path == ""
    assert url.hostname == "ci.kbase.us"
    assert url.fragment == "orcidlink/error"
    # assert url.query
    query = parse_qs(url.query)
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
