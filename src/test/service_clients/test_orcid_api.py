import json
from test.mocks.data import load_data_file, load_test_data
from test.mocks.mock_contexts import (
    mock_orcid_api_service,
    mock_orcid_api_service_with_errors,
    mock_orcid_oauth_service,
    mock_orcid_oauth_service2,
    no_stderr,
)

import aiohttp
import httpx
import pytest

from orcidlink.lib import errors, utils
from orcidlink.lib.config import config
from orcidlink.lib.service_clients import orcid_api

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file(utils.module_path("deploy/config.toml"), contents=config_yaml)
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


@pytest.fixture(scope="function")
def my_fs(fs):
    yield fs


def test_orcid_api_url(fake_fs):
    config(reload=True)
    value = orcid_api.orcid_api_url("path")
    assert isinstance(value, str)
    assert value == "https://api.sandbox.orcid.org/v3.0/path"


def test_orcid_api():
    value = orcid_api.orcid_api("token")
    assert isinstance(value, orcid_api.ORCIDAPIClient)
    assert value.access_token == "token"


def test_orcid_oauth():
    value = orcid_api.orcid_oauth("token")
    assert isinstance(value, orcid_api.ORCIDOAuthClient)
    assert value.access_token == "token"


def test_orcid_oauth():
    value = orcid_api.orcid_oauth("token")
    assert isinstance(value, orcid_api.ORCIDOAuthClient)
    assert value.access_token == "token"


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


def test_ORCIDOAuthClient_url():
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    url = client.url("foo")
    assert url == "url/foo"


def test_ORCIDOAuthClient_header():
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    header = client.header()
    assert isinstance(header, dict)
    assert header.get("Accept") == "application/vnd.orcid+json"
    assert header.get("Content-Type") == "application/vnd.orcid+json"
    assert header.get("Authorization") == "Bearer access_token"


class FakeResponse:
    def __init__(self, status_code: int = None, text: str = None):
        self.status_code = status_code
        self.text = text


def test_ORCIDAuthClient_make_upstream_errorxx():
    #
    # Error response in expected form, with a JSON response including "error_description"
    #

    with pytest.raises(errors.ServiceErrorXX) as exx:
        raise errors.ServiceErrorXX(errors.NOT_FOUND, "ORCID User Profile Not Found")
    assert exx.value.error_code.status_code == errors.NOT_FOUND.status_code
    assert exx.value.message == "ORCID User Profile Not Found"


def test_ORCIDAuthClient_make_upstream_error():
    #
    # Error response in expected form, with a JSON response including "error_description"
    #
    error_result = {"error_description": "bar"}
    status_code = 123

    with pytest.raises(errors.ServiceErrorX) as ex:
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

    assert ex.value.status_code == 502
    assert ex.value.data["source"] == "source"
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

    with pytest.raises(errors.ServiceErrorX) as ex:
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

    assert ex.value.status_code == 502
    assert ex.value.data["source"] == "source"
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

    with pytest.raises(errors.ServiceErrorX) as ex:
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

    assert ex.value.status_code == 502
    assert ex.value.data["source"] == "source"
    # TODO: more error properties
    # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
    # assert ex.value.error.data["originalResponseJSON"]["foo"] == "foe"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Finally, we need to be able to handle no-content responses from ORCID.
    #
    error_result = None
    status_code = 401

    with pytest.raises(errors.ServiceErrorX) as ex:
        raise orcid_api.make_upstream_error(status_code, error_result, "source")

    assert ex.value.status_code == 502
    assert ex.value.data["source"] == "source"
    # TODO: more error properties
    # assert "originalResponseJSON" not in ex.value.error.data
    # assert ex.value.error.data["originalResponseText"] == "just text, folks"


async def test_ORCIDOAuth_success():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            response = await client.revoke_token()
            assert response is None


async def test_ORCIDOAuth_error():
    with no_stderr():
        with mock_orcid_oauth_service2() as [_, _, url]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.ServiceErrorX):
                await client.revoke_token()


async def test_exchange_code_for_token():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "foo"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            response = await client.exchange_code_for_token(code)
            assert response.access_token == "access_token_for_foo"


async def test_exchange_code_for_token_no_content_type():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "no-content-type"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "No content-type in response"


async def test_exchange_code_for_token_not_json_content():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "not-json-content"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Error decoding JSON response"


async def test_exchange_code_for_token_not_json_content_type():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "not-json-content-type"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Expected JSON response, got foo-son"


async def test_exchange_code_for_token_error_incorrect_error_format():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "error-incorrect-error-format"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "Unexpected Error Response from ORCID"


async def test_exchange_code_for_token_error_correct_error_format():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            code = "error-correct-error-format"
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(errors.UpstreamError) as ie:
                await client.exchange_code_for_token(code)
            assert ie.value.message == "a description of some error"


#
# ORCID API
#


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


def test_ORCIDAPIClient_url():
    client = orcid_api.ORCIDAPIClient(url="url", access_token="access_token")
    url = client.url("foo")
    assert url == "url/foo"


def test_ORCIDAPIClient_header():
    client = orcid_api.ORCIDAPIClient(url="url", access_token="access_token")
    header = client.header()
    assert isinstance(header, dict)
    assert header.get("Accept") == "application/vnd.orcid+json"
    assert header.get("Content-Type") == "application/vnd.orcid+json"
    assert header.get("Authorization") == "Bearer access_token"


async def test_ORCIDAPI_get_profile():
    with no_stderr():
        with mock_orcid_api_service() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            profile = await client.get_profile(orcid_id)
            assert isinstance(profile, orcid_api.ORCIDProfile)
            assert profile.orcid_identifier.path == orcid_id


async def test_ORCIDAPI_get_profile_not_found():
    """
    If an ORCID profile is not found upstream, we expect a general purpose ServiceError
    with a status code of 404 and an error code of notFound
    """
    with no_stderr():
        with mock_orcid_api_service_with_errors() as [_, _, url]:
            # Just alter the final 6 to 7 so that it doesn't match any testing orcid
            # profiles.
            orcid_id = "0000-0003-4997-3077"
            with pytest.raises(errors.ServiceErrorXX):
                client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
                await client.get_profile(orcid_id)


async def test_ORCIDAPI_get_profile_not_authorized():
    with no_stderr():
        with mock_orcid_api_service_with_errors() as [_, _, url]:
            # Just alter the final 6 to 7 so that it doesn't match any testing orcid
            # profiles.
            orcid_id = "trigger-401"
            with pytest.raises(errors.ServiceErrorXX):
                client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
                await client.get_profile(orcid_id)


async def test_ORCIDAPI_get_works():
    with no_stderr():
        with mock_orcid_api_service() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            works = await client.get_works(orcid_id)
            assert isinstance(works, orcid_api.Works)
            assert works.group[0].work_summary[0].put_code == 1487805


async def test_ORCIDAPI_get_works_error():
    with no_stderr():
        with mock_orcid_api_service_with_errors() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(errors.ServiceErrorX):
                await client.get_works(orcid_id)


async def test_ORCIDAPI_save_work():
    with no_stderr():
        with mock_orcid_api_service() as [_, _, url]:
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
            work_update = load_test_data("orcid", f"work_{str(put_code)}")["bulk"][0][
                "work"
            ]
            # don't change anything for now
            result = await client.save_work(
                orcid_id, put_code, orcid_api.Work.model_validate(work_update)
            )
            assert isinstance(result, orcid_api.Work)
            assert result.put_code == put_code


async def test_ORCIDAPI_save_work_error():
    #
    # We use the mock ORCID server which returns errors
    #
    with no_stderr():
        with mock_orcid_api_service_with_errors() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            #
            # The client we are testing will access the mock server above since we are
            # using the base_url it calculates, which uses IP 127.0.0.1 as specified in the
            # constructor, and a randomly generated port.
            #
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(errors.ServiceErrorX) as ex:
                put_code = 1526002
                work_update = orcid_api.Work.model_validate(
                    load_test_data("orcid", f"work_{str(put_code)}")["bulk"][0]["work"]
                )
                # don't change anything for now
                await client.save_work(orcid_id, put_code, work_update)
            # assert ex.value.error.data["originalResponseJSON"]["response-code"] == 400

            assert ex.value.code == "upstreamError"
            assert ex.value.title == "Upstream Error"
            assert ex.value.data["source"] == "save_work"
            assert ex.value.data["status_code"] == 500
            # assert ex.value.error.response_code == 400
            # assert ex.value.error.data.status_code == 400


def test_make_upstream_error_401():
    # A 401 from ORCID
    error_content = {"error": "My Error", "error_description": "Should not see me"}
    status_code = 401

    result = orcid_api.make_upstream_error(status_code, error_content, "foo")
    assert isinstance(result, errors.ServiceErrorX)
    assert result.status_code == 502
    assert result.code == "upstreamError"
    assert result.title == "Upstream Error"
    assert result.data["source"] == "foo"
    assert result.data["detail"]["error"] == "My Error"
    assert result.data["detail"].get("error_description") is None
    # assert "error_description" not in result.error.data.detail


def test_make_upstream_error_non_401():
    error_content = {
        "response-code": 123,
        "developer-message": "My Developer Message",
        "user-message": "My User Message",
        "error-code": 456,
        "more-info": "My More Info",
    }
    status_code = 400

    result = orcid_api.make_upstream_error(status_code, error_content, "foo")
    assert isinstance(result, errors.ServiceErrorX)
    assert result.status_code == 502
    assert result.code == "upstreamError"
    assert result.title == "Upstream Error"
    assert result.data["source"] == "foo"
    assert result.data["detail"]["response-code"] == 123
    # assert result.error.data.detail.error_description is None
    # assert "error_description" not in result.error.data.detail


def test_make_upstream_error_internal_server():
    error_content = {
        "message-version": "123",
        "orcid-profile": None,
        "orcid-search-results": None,
        "error-desc": {"value": "My error desc"},
    }
    status_code = 500

    result = orcid_api.make_upstream_error(status_code, error_content, "foo")
    assert isinstance(result, errors.ServiceErrorX)
    assert result.status_code == 502
    assert result.code == "upstreamError"
    assert result.title == "Upstream Error"
    assert result.data["source"] == "foo"
    assert result.data["detail"]["message-version"] == "123"
    # assert result.error.data.detail.error_description is None
    # assert "error_description" not in result.error.data.detail
