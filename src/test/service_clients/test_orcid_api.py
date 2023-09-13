import os
from test.mocks.data import load_test_data
from test.mocks.env import MOCK_ORCID_API_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_orcid_api_service,
    mock_orcid_api_service_with_errors,
    mock_orcid_oauth_service,
    mock_orcid_oauth_service2,
    no_stderr,
)
from unittest import mock

import pytest

from orcidlink.lib import exceptions
from orcidlink.lib.errors import ERRORS
from orcidlink.lib.service_clients import orcid_api

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
    value = orcid_api.orcid_oauth("token")
    assert isinstance(value, orcid_api.ORCIDOAuthClient)
    assert value.access_token == "token"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_constructor():
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    assert client.base_url == "url"
    assert client.access_token == "access_token"

    with pytest.raises(
        TypeError, match='the "access_token" named parameter is required'
    ):
        orcid_api.ORCIDOAuthClient(url="url")

    with pytest.raises(TypeError, match='the "url" named parameter is required'):
        orcid_api.ORCIDOAuthClient(access_token="access_token")

    with pytest.raises(TypeError, match='the "url" named parameter is required'):
        orcid_api.ORCIDOAuthClient()


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_url():
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    url = client.url("foo")
    assert url == "url/foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDOAuthClient_header():
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    header = client.header()
    assert isinstance(header, dict)
    assert header.get("Accept") == "application/vnd.orcid+json"
    assert header.get("Content-Type") == "application/vnd.orcid+json"
    assert header.get("Authorization") == "Bearer access_token"


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
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

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
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

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
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

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
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

    # assert ex.value.status_code == 502
    assert ex.value.data is not None and ex.value.data.source == "source"
    # TODO: more error properties
    # assert "originalResponseJSON" not in ex.value.error.data
    # assert ex.value.error.data["originalResponseText"] == "just text, folks"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDOAuth_success():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            response = await client.revoke_token()
            assert response is None


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDOAuth_error():
    with no_stderr():
        with mock_orcid_oauth_service2(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.ServiceErrorY):
                await client.revoke_token()


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "foo"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            response = await client.exchange_code_for_token(code)
            assert response.access_token == "access_token_for_foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_no_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "no-content-type"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "No content-type in response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.JSONDecodeError):
                await client.exchange_code_for_token(code)
            # assert ie.value.message == "Error decoding JSON response"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_not_json_content_type():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "not-json-content-type"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Expected JSON response, got foo-son"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_incorrect_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-incorrect-error-format"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Unexpected Error Response from ORCID"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_exchange_code_for_token_error_correct_error_format():
    with no_stderr():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT) as [_, _, url, port]:
            code = "error-correct-error-format"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "a description of some error"


#
# ORCID API
#


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDAPIClient_constructor():
    client = orcid_api.ORCIDAPIClient(url="url", access_token="access_token")
    assert client.base_url == "url"
    assert client.access_token == "access_token"

    with pytest.raises(
        TypeError, match='the "access_token" named parameter is required'
    ):
        orcid_api.ORCIDAPIClient(url="url")

    with pytest.raises(TypeError, match='the "url" named parameter is required'):
        orcid_api.ORCIDAPIClient(access_token="access_token")

    with pytest.raises(TypeError, match='the "url" named parameter is required'):
        orcid_api.ORCIDAPIClient()


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDAPIClient_url():
    client = orcid_api.ORCIDAPIClient(url="url", access_token="access_token")
    url = client.url("foo")
    assert url == "url/foo"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_ORCIDAPIClient_header():
    client = orcid_api.ORCIDAPIClient(url="url", access_token="access_token")
    header = client.header()
    assert isinstance(header, dict)
    assert header.get("Accept") == "application/vnd.orcid+json"
    assert header.get("Content-Type") == "application/vnd.orcid+json"
    assert header.get("Authorization") == "Bearer access_token"


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_profile():
    with no_stderr():
        with mock_orcid_api_service(MOCK_ORCID_API_PORT) as [_, _, url, port]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            profile = await client.get_profile(orcid_id)
            assert isinstance(profile, orcid_api.ORCIDProfile)
            assert profile.orcid_identifier.path == orcid_id


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_profile_not_found():
    """
    If an ORCID profile is not found upstream, we expect a general purpose ServiceError
    with a status code of 404 and an error code of notFound
    """
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            # Just alter the final 6 to 7 so that it doesn't match any testing orcid
            # profiles.
            orcid_id = "0000-0003-4997-3077"
            with pytest.raises(exceptions.ServiceErrorY):
                client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
                await client.get_profile(orcid_id)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_profile_not_authorized():
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            # Just alter the final 6 to 7 so that it doesn't match any testing orcid
            # profiles.
            orcid_id = "trigger-401"
            with pytest.raises(exceptions.ServiceErrorY):
                client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
                await client.get_profile(orcid_id)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_profile_other_error():
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            # Just alter the final 6 to 7 so that it doesn't match any testing orcid
            # profiles.
            orcid_id = "trigger-415"
            with pytest.raises(exceptions.ServiceErrorY):
                client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
                await client.get_profile(orcid_id)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_works():
    with no_stderr():
        with mock_orcid_api_service(MOCK_ORCID_API_PORT) as [_, _, url, port]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            works = await client.get_works(orcid_id)
            assert isinstance(works, orcid_api.Works)
            assert works.group[0].work_summary[0].put_code == 1487805


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_get_works_error():
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.ServiceErrorY):
                await client.get_works(orcid_id)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_work():
    with no_stderr():
        with mock_orcid_api_service(MOCK_ORCID_API_PORT) as [_, _, url, port]:
            orcid_id = "0000-0003-4997-3076"
            put_code = 1526002
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            work = await client.get_work(orcid_id, put_code)
            assert isinstance(work, orcid_api.GetWorkResult)
            assert work.bulk[0].work.put_code == put_code


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_get_work_error():
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            orcid_id = "0000-0003-4997-3076"
            put_code = 1526002
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.ServiceErrorY):
                await client.get_work(orcid_id, put_code)


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_save_work():
    with no_stderr():
        with mock_orcid_api_service(MOCK_ORCID_API_PORT) as [_, _, url, port]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            # work_update: WorkUpdate(
            #     putCode="1487805",
            #     title="foo",
            #     journal="bar",
            #     date="2001/02/03",Ω
            #     workType="baz",
            #     url="some url",
            # )
            # TODO: external ids too!
            put_code = 1526002
            work_update = load_test_data(
                TEST_DATA_DIR, "orcid", f"work_{str(put_code)}"
            )["bulk"][0]["work"]
            # don't change anything for now
            result = await client.save_work(
                orcid_id, put_code, orcid_api.WorkUpdate.model_validate(work_update)
            )
            assert isinstance(result, orcid_api.Work)
            assert result.put_code == put_code


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
async def test_ORCIDAPI_save_work_error(fake_fs):
    #
    # We use the mock ORCID server which returns errors
    #
    with no_stderr():
        with mock_orcid_api_service_with_errors(MOCK_ORCID_API_PORT) as [
            _,
            _,
            url,
            port,
        ]:
            orcid_id = "0000-0003-4997-3076"
            #
            # The client we are testing will access the mock server above since we are
            # using the base_url it calculates, which uses IP 127.0.0.1 as specified in
            # the constructor, and a randomly generated port.
            #
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(exceptions.UpstreamORCIDAPIError) as ex:
                put_code = 1526002
                work_update = orcid_api.WorkUpdate.model_validate(
                    load_test_data(TEST_DATA_DIR, "orcid", f"work_{str(put_code)}")[
                        "bulk"
                    ][0]["work"]
                )
                # don't change anything for now
                await client.save_work(orcid_id, put_code, work_update)
            # assert ex.value.error.data["originalResponseJSON"]["response-code"] == 400

            assert ex.value.error.code == ERRORS.upstream_orcid_error.code
            assert ex.value.error.title == "Upstream ORCID Error"
            assert ex.value.data is not None and ex.value.data.source == "save_work"
            assert ex.value.data.status_code == 500
            # assert ex.value.error.response_code == 400
            # assert ex.value.error.data.status_code == 400


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_make_upstream_error_401(fake_fs):
    # A 401 from ORCID
    error_content = {"error": "My Error", "error_description": "Should not see me"}
    status_code = 401

    result = orcid_api.make_upstream_error(status_code, error_content, "foo")
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

        result = orcid_api.make_upstream_error(status_code, error_content, "foo")
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

        result = orcid_api.make_upstream_error(status_code, error_content, "foo")
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
