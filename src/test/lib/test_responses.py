import json
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib import responses
from orcidlink.lib.responses import ErrorException, error_response_not_found
from test.data.utils import load_data_file

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


def test_success_response_no_data():
    value = responses.success_response_no_data()
    assert isinstance(value, Response)
    assert value.status_code == 204


def test_make_error():
    error = responses.make_error("code", "title", "message", "some data")
    assert isinstance(error, responses.ErrorResponse)
    assert error.code == "code"
    assert error.title == "title"
    assert error.message == "message"
    assert error.data == "some data"

    error = responses.make_error(100, "title", "message")
    error.data is None


def test_error_response():
    value = responses.error_response(
        "code", "title", "message", data={"some": "data"}, status_code=123
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
            "code", "title", ex, data={"some": "data"}, status_code=123
        )
        assert isinstance(value, JSONResponse)
        assert value.status_code == 123
        # The JSONResponse structure is not in scope for this project; it is simply provided to
        # fastapi which utilizes it for the response.
        # Still, the whole point of testing this is to assure ourselves that the response is as we expect,
        # so ... here we go.
        assert value.body is not None
        data = json.loads(value.body)
        assert data["code"] == "code"
        assert data["title"] == "title"
        assert data["message"] == "I am exceptional"
        assert data["data"]["some"] == "data"
        assert data["data"]["exception"] == "I am exceptional"
        assert isinstance(data["data"]["traceback"], list)


def test_exception_error_response_no_data():
    try:
        raise Exception("I am exceptional")
    except Exception as ex:
        value = responses.exception_error_response("code", "title", ex, status_code=123)
        assert isinstance(value, JSONResponse)
        assert value.status_code == 123
        # The JSONResponse structure is not in scope for this project; it is simply provided to
        # fastapi which utilizes it for the response.
        # Still, the whole point of testing this is to assure ourselves that the response is as we expect,
        # so ... here we go.
        assert value.body is not None
        data = json.loads(value.body)
        assert data["code"] == "code"
        assert data["title"] == "title"
        assert data["message"] == "I am exceptional"
        assert data["data"]["exception"] == "I am exceptional"
        assert isinstance(data["data"]["traceback"], list)


def test_ui_error_response(fake_fs):
    value = responses.ui_error_response("code", "title", "message")
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
    assert query["code"] == ["code"]

    # assert data["code"] == "code"
    # assert data["title"] == "title"
    # assert data["message"] == "message"


def test_make_error_exception():
    with pytest.raises(ErrorException, match="message") as ex:
        raise responses.make_error_exception(
            "code", "title", "message", data={"foo": "bar"}, status_code=123
        )

    response = ex.value.get_response()
    assert response is not None
    assert response.status_code == 123


def test_ensure_authorization():
    value = responses.ensure_authorization("foo")
    assert value == "foo"

    with pytest.raises(
            ErrorException, match="API call requires a KBase auth token"
    ) as ex:
        responses.ensure_authorization(None)


def test_error_response_not_found():
    value = error_response_not_found("Foo not found")

    assert isinstance(value, JSONResponse)
    assert value.status_code == 404
    # the response body is bytes, which we can convert
    # back to a dict...
    body_json = json.loads(value.body)
    assert isinstance(body_json, dict)
    assert body_json["code"] == "not-found"
    assert body_json["title"] == "Not Found"
    assert body_json["message"] == "Foo not found"
