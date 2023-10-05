import os
from test.mocks.env import MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (  # mock_orcid_oauth_service2,
    mock_orcid_oauth_service,
    no_stderr,
)
from unittest import mock

import pytest

from orcidlink.jsonrpc.errors import (
    ContentTypeError,
    JSONDecodeError,
    NotAuthorizedError,
    UpstreamError,
)
from orcidlink.lib.responses import UIError

# from orcidlink.lib import exceptions
from orcidlink.lib.service_clients import orcid_api
from orcidlink.lib.service_clients.orcid_oauth import ORCIDOAuthClient, orcid_oauth
from orcidlink.lib.service_clients.orcid_oauth_interactive import (
    ORCIDOAuthInteractiveClient,
)

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


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_ORCIDAuthClient_make_upstream_errorxx():
#     #
#     # Error response in expected form, with a JSON response including
#     # "error_description"
#     #

#     with pytest.raises(exceptions.ServiceErrorY) as exx:
#         raise exceptions.NotFoundError("ORCID User Profile Not Found")
#     # assert exx.value.status_code == 404
#     assert exx.value.error.code == ERRORS.not_found.code
#     assert exx.value.message == "ORCID User Profile Not Found"


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_ORCIDAuthClient_make_upstream_error():
#     #
#     # Error response in expected form, with a JSON response including
#     # "error_description"
#     #
#     error_result = {"error_description": "bar"}
#     status_code = 123

#     with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
#         raise exceptions.make_upstream_error(status_code, error_result, "source")

#     # assert ex.value.status_code == 502
#     assert ex.value.data is not None and ex.value.data.source == "source"
#     # TODO: more error properties
#     # assert ex.value.error.data["originalResponseJSON"]["error_description"] == "bar"
#     # assert "originalResponseText" not in ex.value.error.data

#     #
#     # Error response in expected form, with a JSON response without "error_description";
#     # Note that we don't make assumptions about any other field, and in this case, only
#     # in the case of a 401 or 403 status code, in order to remove private information.
#     #
#     error_result = {"foo": "bar"}
#     status_code = 123

#     with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
#         raise exceptions.make_upstream_error(status_code, error_result, "source")

#     # assert ex.value.status_code == 502
#     assert ex.value.data is not None and ex.value.data.source == "source"
#     # TODO: more error properties
#     # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
#     # assert ex.value.error.data["originalResponseJSON"]["foo"] == "bar"
#     # assert "originalResponseText" not in ex.value.error.data

#     #
#     # Error response in expected form, with a JSON response without "error_description";
#     # Note that we don't make assumptions about any other field, and in this case, only
#     # in the case of a 401 or 403 status code, in order to remove private information.
#     #
#     error_result = {"error_description": "bar", "foo": "foe"}
#     status_code = 401

#     with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
#         raise exceptions.make_upstream_error(status_code, error_result, "source")

#     # assert ex.value.status_code == 502
#     assert ex.value.data is not None and ex.value.data.source == "source"
#     # TODO: more error properties
#     # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
#     # assert ex.value.error.data["originalResponseJSON"]["foo"] == "foe"
#     # assert "originalResponseText" not in ex.value.error.data

#     #
#     # Finally, we need to be able to handle no-content responses from ORCID.
#     #
#     error_result = None
#     status_code = 401

#     with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
#         raise exceptions.make_upstream_error(status_code, error_result, "source")

#     # assert ex.value.status_code == 502
#     assert ex.value.data is not None and ex.value.data.source == "source"
#     # TODO: more error properties
#     # assert "originalResponseJSON" not in ex.value.error.data
#     # assert ex.value.error.data["originalResponseText"] == "just text, folks"

#
# Revoke token
#


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_success():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            response = await client.revoke_access_token("access_token")
            assert response is None


# This test doesn't make any sense -- the error is not thrown
@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_not_authorized_error():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(NotAuthorizedError):
                await client.revoke_access_token("unauthorized_access_token")


# This test doesn't make any sense -- the error is not thrown
@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_other_upstream_error():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.revoke_access_token("other_error_access_token")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_no_content_length():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.revoke_access_token("no-content-length")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_non_empty_response():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.revoke_access_token("non-empty-response")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_no_content_type():
    """
    Although the normal response is empty and doesn't care about a content-type
    being present or not, for an error condition it must have a content type
    (and in the test below, it must be application/json)
    """
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(ContentTypeError):
                await client.revoke_access_token("error-response-no-content-type")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_not_json_content_type():
    """
    Although the normal response is empty and doesn't care about a content-type
    being present or not, for an error condition it must be application/json.
    """
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(ContentTypeError):
                await client.revoke_access_token("error-response-not-json-content-type")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_not_json():
    """
    Although the normal response is empty and doesn't care about a content-type
    being present or not, for an error condition it must be application/json.
    """
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(JSONDecodeError):
                await client.revoke_access_token("error-response-not-json")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_error_invalid_json():
    """
    Although the normal response is empty and doesn't care about a content-type
    being present or not, for an error condition it must be application/json.
    """
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.revoke_access_token("error-response-invalid-json")


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_no_content_type():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             client = ORCIDOAuthClient(url)
#             with pytest.raises(UIError) as ie:
#                 await client.revoke_access_token("no-content-type")
#             assert ie.value.code == ContentTypeError.CODE
#             # assert ie.value.message == "No content-type in response"


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_no_content_length():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             client = ORCIDOAuthInteractiveClient(url)
#             with pytest.raises(UIError) as ie:
#                 await client.revoke_access_token("no-content-length")
#             assert ie.value.code == UpstreamError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_empty_content():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "empty-content"
#             client = ORCIDOAuthInteractiveClient(url)
#             with pytest.raises(UIError) as uie:
#                 await client.revoke_access_token(code)
#             assert uie.value.code == UpstreamError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def ttest_orcid_oauth_revoke_access_token_not_json_content():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "not-json-content"
#             client = ORCIDOAuthInteractiveClient(url)
#             with pytest.raises(UIError) as err:
#                 await client.revoke_access_token(code)
#             assert err.value.code == JSONDecodeError.CODE
#             # assert ie.value.message == "Error decoding JSON response"


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_not_json_content_type():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "not-json-content-type"
#             client = ORCIDOAuthInteractiveClient(url)
#             with pytest.raises(UIError) as uie:
#                 await client.revoke_access_token(code)
#             assert uie.value.code == ContentTypeError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_error_incorrect_error_format():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "error-incorrect-error-format"
#             client = ORCIDOAuthInteractiveClient(url=url)
#             with pytest.raises(UIError) as uie:
#                 await client.revoke_access_token(code)
#             assert uie.value.code == UpstreamError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_error_correct_error_format():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "error-correct-error-format"
#             client = ORCIDOAuthInteractiveClient(url=url)
#             with pytest.raises(UIError) as uie:
#                 await client.exchange_code_for_token(code)
#             assert uie.value.code == UpstreamError.CODE


#
# Exchange code for token
#


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "foo"
            client = ORCIDOAuthInteractiveClient(url)
            response = await client.exchange_code_for_token(code)
            assert response.access_token == "access_token_for_foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_no_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "no-content-type"
            client = ORCIDOAuthInteractiveClient(url)
            with pytest.raises(UIError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.code == ContentTypeError.CODE
            # assert ie.value.message == "No content-type in response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_no_content_length():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "no-content-length"
            client = ORCIDOAuthInteractiveClient(url)
            with pytest.raises(UIError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.code == UpstreamError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_empty_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "empty-content"
            client = ORCIDOAuthInteractiveClient(url)
            with pytest.raises(UIError) as uie:
                await client.exchange_code_for_token(code)
            assert uie.value.code == UpstreamError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content"
            client = ORCIDOAuthInteractiveClient(url)
            with pytest.raises(UIError) as err:
                await client.exchange_code_for_token(code)
            assert err.value.code == JSONDecodeError.CODE
            # assert ie.value.message == "Error decoding JSON response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content-type"
            client = ORCIDOAuthInteractiveClient(url)
            with pytest.raises(UIError) as uie:
                await client.exchange_code_for_token(code)
            assert uie.value.code == ContentTypeError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_incorrect_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-incorrect-error-format"
            client = ORCIDOAuthInteractiveClient(url=url)
            with pytest.raises(UIError) as uie:
                await client.exchange_code_for_token(code)
            assert uie.value.code == UpstreamError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_correct_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-correct-error-format"
            client = ORCIDOAuthInteractiveClient(url=url)
            with pytest.raises(UIError) as uie:
                await client.exchange_code_for_token(code)
            assert uie.value.code == UpstreamError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_make_upstream_error_401(fake_fs):
#     # A 401 from ORCID
#     error_content = {"error": "My Error", "error_description": "Should not see me"}
#     status_code = 401

#     result = exceptions.make_upstream_error(status_code, error_content, "foo")
#     assert isinstance(result, exceptions.UpstreamORCIDAPIError)
#     # assert result.status_code == 502
#     assert result.error.code == 1052
#     assert result.error.title == "Upstream ORCID Error"
#     assert result.data is not None and result.data.source == "foo"
#     assert (
#         isinstance(result.data.detail, dict)
#         and result.data.detail["error"] is not None
#         and result.data.detail["error"] == "My Error"
#     )
#     assert result.data.detail.get("error_description") is None
#     # assert "error_description" not in result.error.data.detail


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# def test_make_upstream_error_non_401(fake_fs):
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         error_content = {
#             "response-code": 123,
#             "developer-message": "My Developer Message",
#             "user-message": "My User Message",
#             "error-code": 456,
#             "more-info": "My More Info",
#         }
#         status_code = 400

#         result = exceptions.make_upstream_error(status_code, error_content, "foo")
#         assert isinstance(result, exceptions.ServiceErrorY)
#         # assert result.status_code == 502
#         assert result.error.code == exceptions.ERRORS.upstream_orcid_error.code
#         assert result.error.title == "Upstream ORCID Error"
#         assert (
#             isinstance(result.data, exceptions.UpstreamErrorData)
#             and result.data.source == "foo"
#         )
#         # assert isinstance(result.data['detail'], dict) and result.data["detail"]["response-code"] == 123
#         # assert result.error.data.detail.error_description is None
#         # assert "error_description" not in result.error.data.detail


# def test_make_upstream_error_internal_server(fake_fs):
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         error_content = {
#             "message-version": "123",
#             "orcid-profile": None,
#             "orcid-search-results": None,
#             "error-desc": {"value": "My error desc"},
#         }
#         status_code = 500

#         result = exceptions.make_upstream_error(status_code, error_content, "foo")
#         assert isinstance(result, exceptions.ServiceErrorY)
#         # assert result.status_code == 502
#         assert result.error.code == exceptions.ERRORS.upstream_orcid_error.code
#         assert result.error.title == "Upstream ORCID Error"
#         assert (
#             isinstance(result.data, exceptions.UpstreamErrorData)
#             and result.data.source == "foo"
#         )
#         # assert isinstance(result.data['detail'], dict) and
# result.data["detail"]["message-version"] == "123"
#         # assert result.error.data.detail.error_description is None
# assert "error_description" not in result.error.data.detail

#
# Refresh token
#


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_refresh_token():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            response = await client.refresh_token("refresh-token-foo")
            assert response is not None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_refresh_token_error_not_authorized():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(NotAuthorizedError):
                await client.refresh_token("refresh-token-unauthorized")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_refresh_token_error_other_error():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.refresh_token("refresh-token-other-error")


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_refresh_token_error_no_content_length():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             client = ORCIDOAuthClient(url)
#             with pytest.raises(UpstreamError):
#                 await client.refresh_token("no-content-length")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_refresh_token_error_no_content_length():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.refresh_token("no-content-length")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_no_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(ContentTypeError):
                await client.refresh_token("no-content-type")


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_no_content_length():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             client = ORCIDOAuthClient(url)
#             with pytest.raises(UIError) as ie:
#                 await client.refresh_token("no-content-length")
#             assert ie.value.code == UpstreamError.CODE


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_empty_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.refresh_token("empty-content")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_not_json_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(JSONDecodeError):
                await client.refresh_token("not-json-content")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_not_json_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(ContentTypeError):
                await client.refresh_token("not-json-content-type")


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_orcid_oauth_revoke_access_token_invalid_error():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = ORCIDOAuthClient(url)
            with pytest.raises(UpstreamError):
                await client.refresh_token("invalid-error")


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_error_incorrect_error_format():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             code = "error-incorrect-error-format"
#             client = ORCIDOAuthClient(url=url)
#             with pytest.raises(UIError) as uie:
#                 await client.refresh_token(code)
#             assert uie.value.code == UpstreamError.CODE


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
# async def test_orcid_oauth_revoke_access_token_error_correct_error_format():
#     with no_stderr():
#         with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
#             client = ORCIDOAuthClient(url=url)
#             with pytest.raises(UIError) as uie:
#                 await client.refresh_token("error-correct-error-format")
#             assert uie.value.code == UpstreamError.CODE
