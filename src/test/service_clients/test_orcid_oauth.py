import os
from test.mocks.env import MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_orcid_oauth_service,
    mock_orcid_oauth_service2,
    no_stderr,
)
from unittest import mock

import pytest

from orcidlink.lib import exceptions
from orcidlink.lib.errors import ERRORS
from orcidlink.lib.service_clients import orcid_api
from orcidlink.lib.service_clients.orcid_oauth import ORCIDOAuthClient, orcid_oauth

# Set up test data here; otherwise the ENV mocking interferes with the
# TEST_DATA_DIR env var which points to the location of test data!

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
    yield fs


@pytest.fixture(scope="function")
def my_fs(fs):
    yield fs


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_orcid_api_url(fake_fs):
    value = orcid_api.orcid_api_url("path")
    assert isinstance(value, str)
    assert value == f"{TEST_ENV['ORCID_API_BASE_URL']}/path"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_orcid_api():
    value = orcid_api.orcid_api("token")
    assert isinstance(value, orcid_api.ORCIDAPIClient)
    assert value.access_token == "token"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_orcid_oauth():
    value = orcid_oauth()
    assert isinstance(value, ORCIDOAuthClient)
    # assert isinstance(value.url, str)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_constructor():
    client = ORCIDOAuthClient("url")
    assert client.base_url == "url"

    with pytest.raises(TypeError, match='the "url" named parameter is required'):
        ORCIDOAuthClient()


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_url():
    client = ORCIDOAuthClient(url="url")
    url = client.url_path("foo")
    assert url == "url/foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_header():
    client = ORCIDOAuthClient(url="url")
    header = client.header()
    assert header.get("accept") == "application/json"
    assert header.get("content-type") == "application/x-www-form-urlencoded"


class FakeResponse:
    def __init__(self, status_code: int | None = None, text: str | None = None):
        self.status_code = status_code
        self.text = text


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDAuthClient_make_upstream_errorxx():
    #
    # Error response in expected form, with a JSON response including
    # "error_description"
    #

    with pytest.raises(exceptions.ServiceErrorY) as exx:
        raise exceptions.NotFoundError("ORCID User Profile Not Found")
    # assert exx.value.status_code == 404
    assert exx.value.error.code == ERRORS.not_found.code
    assert exx.value.message == "ORCID User Profile Not Found"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDAuthClient_make_upstream_error():
    #
    # Error response in expected form, with a JSON response including
    # "error_description"
    #
    error_result = {"error_description": "bar"}
    status_code = 123

    with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
        raise exceptions.make_upstream_error(status_code, error_result, "source")

    # assert ex.value.status_code == 502
    assert ex.value.data is not None and ex.value.data.source == "source"
    # TODO: more error properties
    # assert ex.value.error.data["originalResponseJSON"]["error_description"] == "bar"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Error response in expected form, with a JSON response without "error_description";
    # Note that we don't make assumptions about any other field, and in this case, only
    # in the case of a 401 or 403 status code, in order to remove private information.
    #
    error_result = {"foo": "bar"}
    status_code = 123

    with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
        raise exceptions.make_upstream_error(status_code, error_result, "source")

    # assert ex.value.status_code == 502
    assert ex.value.data is not None and ex.value.data.source == "source"
    # TODO: more error properties
    # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
    # assert ex.value.error.data["originalResponseJSON"]["foo"] == "bar"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Error response in expected form, with a JSON response without "error_description";
    # Note that we don't make assumptions about any other field, and in this case, only
    # in the case of a 401 or 403 status code, in order to remove private information.
    #
    error_result = {"error_description": "bar", "foo": "foe"}
    status_code = 401

    with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
        raise exceptions.make_upstream_error(status_code, error_result, "source")

    # assert ex.value.status_code == 502
    assert ex.value.data is not None and ex.value.data.source == "source"
    # TODO: more error properties
    # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
    # assert ex.value.error.data["originalResponseJSON"]["foo"] == "foe"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Finally, we need to be able to handle no-content responses from ORCID.
    #
    error_result = None
    status_code = 401

    with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
        raise exceptions.make_upstream_error(status_code, error_result, "source")

    # assert ex.value.status_code == 502
    assert ex.value.data is not None and ex.value.data.source == "source"
    # TODO: more error properties
    # assert "originalResponseJSON" not in ex.value.error.data
    # assert ex.value.error.data["originalResponseText"] == "just text, folks"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDOAuth_success():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            response = await client.revoke_access_token("access_token")
            assert response is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDOAuth_error():
    with no_stderr():
        with mock_orcid_oauth_service2(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(exceptions.ServiceErrorY):
                await client.revoke_access_token("access_token")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "foo"
            client = ORCIDOAuthClient(url)
            response = await client.exchange_code_for_token(code)
            assert response.access_token == "access_token_for_foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_no_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "no-content-type"
            client = ORCIDOAuthClient(url)
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "No content-type in response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content"
            client = ORCIDOAuthClient(url)
            with pytest.raises(exceptions.JSONDecodeError):
                await client.exchange_code_for_token(code)
            # assert ie.value.message == "Error decoding JSON response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content-type"
            client = ORCIDOAuthClient(url)
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Expected JSON response, got foo-son"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_incorrect_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-incorrect-error-format"
            client = ORCIDOAuthClient(url=url)
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Unexpected Error Response from ORCID"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_correct_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-correct-error-format"
            client = ORCIDOAuthClient(url=url)
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "a description of some error"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_make_upstream_error_401(fake_fs):
    # A 401 from ORCID
    error_content = {"error": "My Error", "error_description": "Should not see me"}
    status_code = 401

    result = exceptions.make_upstream_error(status_code, error_content, "foo")
    assert isinstance(result, exceptions.UpstreamORCIDAPIError)
    # assert result.status_code == 502
    assert result.error.code == 1052
    assert result.error.title == "Upstream ORCID Error"
    assert result.data is not None and result.data.source == "foo"
    assert (
        isinstance(result.data.detail, dict)
        and result.data.detail["error"] is not None
        and result.data.detail["error"] == "My Error"
    )
    assert result.data.detail.get("error_description") is None
    # assert "error_description" not in result.error.data.detail


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_make_upstream_error_non_401(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        error_content = {
            "response-code": 123,
            "developer-message": "My Developer Message",
            "user-message": "My User Message",
            "error-code": 456,
            "more-info": "My More Info",
        }
        status_code = 400

        result = exceptions.make_upstream_error(status_code, error_content, "foo")
        assert isinstance(result, exceptions.ServiceErrorY)
        # assert result.status_code == 502
        assert result.error.code == exceptions.ERRORS.upstream_orcid_error.code
        assert result.error.title == "Upstream ORCID Error"
        assert (
            isinstance(result.data, exceptions.UpstreamErrorData)
            and result.data.source == "foo"
        )
        # assert isinstance(result.data['detail'], dict) and result.data["detail"]["response-code"] == 123
        # assert result.error.data.detail.error_description is None
        # assert "error_description" not in result.error.data.detail


def test_make_upstream_error_internal_server(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        error_content = {
            "message-version": "123",
            "orcid-profile": None,
            "orcid-search-results": None,
            "error-desc": {"value": "My error desc"},
        }
        status_code = 500

        result = exceptions.make_upstream_error(status_code, error_content, "foo")
        assert isinstance(result, exceptions.ServiceErrorY)
        # assert result.status_code == 502
        assert result.error.code == exceptions.ERRORS.upstream_orcid_error.code
        assert result.error.title == "Upstream ORCID Error"
        assert (
            isinstance(result.data, exceptions.UpstreamErrorData)
            and result.data.source == "foo"
        )
        # assert isinstance(result.data['detail'], dict) and result.data["detail"]["message-version"] == "123"
        # assert result.error.data.detail.error_description is None
        # assert "error_description" not in result.error.data.detail
