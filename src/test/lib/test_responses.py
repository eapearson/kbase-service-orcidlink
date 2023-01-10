import json
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.responses import JSONResponse, RedirectResponse, Response
from orcidlink.lib import responses
from orcidlink.lib.responses import ErrorException


@pytest.fixture
def my_config_file(fs):
    fake_config = """
kbase:
  services:
    Auth2:
      url: https://ci.kbase.us/services/auth/api/V2/token
      tokenCacheLifetime: 300000
      tokenCacheMaxSize: 20000
    ServiceWizard:
      url: http://127.0.0.1:9999/services/service_wizard
  uiOrigin: https://ci.kbase.us
  defaults:
    serviceRequestTimeout: 60000
orcid:
  oauthBaseURL: https://sandbox.orcid.org/oauth
  baseURL: https://sandbox.orcid.org
  apiBaseURL: https://api.sandbox.orcid.org/v3.0
env:
  CLIENT_ID: 'REDACTED-CLIENT-ID'
  CLIENT_SECRET: 'REDACTED-CLIENT-SECRET'
  IS_DYNAMIC_SERVICE: 'yes'
    """
    fs.create_file("/kb/module/config/config.yaml", contents=fake_config)
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
    value = responses.error_response("code", "title", "message", data={"some": "data"}, status_code=123)
    assert isinstance(value, JSONResponse)
    assert value.status_code == 123
    # The JSONResponse structure is not in scope for this project; it is simply provided to
    # fastapi which utilizes it for the response
    assert value.body is not None


def test_exception_error_response():
    try:
        raise Exception("I am exceptional")
    except Exception as ex:
        value = responses.exception_error_response("code", "title", ex, data={"some": "data"}, status_code=123)
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
        assert isinstance(data["data"]["traceback"], list)


def test_ui_error_response(my_config_file):
    value = responses.ui_error_response("code", "title", "message")
    assert isinstance(value, RedirectResponse)
    assert value.status_code == 302
    assert 'location' in value.headers
    assert value.headers.get('location').endswith('#orcidlink/error')
    url = urlparse(value.headers.get('location'))
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
        raise responses.make_error_exception("code", "title", "message", data={"foo": "bar"}, status_code=123)

    response = ex.value.get_response()
    assert response is not None
    assert response.status_code == 123


def test_ensure_authorization():
    value = responses.ensure_authorization("foo")
    assert value == "foo"

    with pytest.raises(ErrorException, match="API call requires a KBase auth token") as ex:
        responses.ensure_authorization(None)


def test_text_to_jsonable():
    value = responses.text_to_jsonable('["hello"]')
    assert value == ["hello"]

    with pytest.raises(ErrorException, match="An error was encountered parsing a string into a jsonable value"):
        responses.text_to_jsonable("foo")
