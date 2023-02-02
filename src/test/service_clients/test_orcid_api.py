import json

import httpx
import pytest
from orcidlink.lib.config import config
from orcidlink.lib.errors import ServiceError
from orcidlink.service_clients import orcid_api
# from orcidlink.service_clients.orcid_api import (
#     ORCIDAPIClient,
#     ORCIDOAuthClient,
#     orcid_api,
#     orcid_api_url,
#     orcid_oauth,
# )
from test.mocks.data import load_data_file, load_test_data
from test.mocks.mock_contexts import (
    mock_orcid_api_service,
    mock_orcid_api_service_with_errors,
    mock_orcid_oauth_service,
    mock_orcid_oauth_service2,
    no_stderr,
)

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/deploy/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/test/data")
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


def test_ORCIDAuthClient_make_exception():
    #
    # Error response in expected form, with a JSON response including "error_description"
    #
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    fake_response = FakeResponse(
        status_code=123, text=json.dumps({"error_description": "bar"})
    )

    with pytest.raises(
            ServiceError, match="Error fetching data from ORCID Auth api"
    ) as ex:
        raise orcid_api.make_exception(fake_response, "source")

    assert ex.value.status_code == 400
    assert ex.value.error.data.source == "source"
    # TODO: more error properties
    # assert ex.value.error.data["originalResponseJSON"]["error_description"] == "bar"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Error response in expected form, with a JSON response without "error_description";
    # Note that we don't make assumptions about any other field, and in this case, only
    # in the case of a 401 or 403 status code, in order to remove private information.
    #
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    fake_response = FakeResponse(status_code=123, text=json.dumps({"foo": "bar"}))

    with pytest.raises(
            ServiceError, match="Error fetching data from ORCID Auth api"
    ) as ex:
        raise orcid_api.make_exception(fake_response, "source")

    assert ex.value.status_code == 400
    assert ex.value.error.data.source == "source"
    # TODO: more error properties
    # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
    # assert ex.value.error.data["originalResponseJSON"]["foo"] == "bar"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Error response in expected form, with a JSON response without "error_description";
    # Note that we don't make assumptions about any other field, and in this case, only
    # in the case of a 401 or 403 status code, in order to remove private information.
    #
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    fake_response = FakeResponse(
        status_code=401, text=json.dumps({"error_description": "bar", "foo": "foe"})
    )

    with pytest.raises(
            ServiceError, match="Error fetching data from ORCID Auth api"
    ) as ex:
        raise orcid_api.make_exception(fake_response, "source")

    assert ex.value.status_code == 400
    assert ex.value.error.data.source == "source"
    # TODO: more error properties
    # assert "error_description" not in ex.value.error.data["originalResponseJSON"]
    # assert ex.value.error.data["originalResponseJSON"]["foo"] == "foe"
    # assert "originalResponseText" not in ex.value.error.data

    #
    # Finally, we need to be able to handle non-json responses from ORCID.
    #
    client = orcid_api.ORCIDOAuthClient(url="url", access_token="access_token")
    fake_response = FakeResponse(status_code=401, text="just text, folks")

    with pytest.raises(
            ServiceError, match="Error fetching data from ORCID Auth api"
    ) as ex:
        raise orcid_api.make_exception(fake_response, "source")

    assert ex.value.status_code == 400
    assert ex.value.error.data.source == "source"
    # TODO: more error properties
    # assert "originalResponseJSON" not in ex.value.error.data
    # assert ex.value.error.data["originalResponseText"] == "just text, folks"


def test_ORCIDOAuth_success():
    with no_stderr():
        with mock_orcid_oauth_service() as [_, _, url]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            response = client.revoke_token()
            assert response is None


def test_ORCIDOAuth_error():
    with no_stderr():
        with mock_orcid_oauth_service2() as [_, _, url]:
            client = orcid_api.ORCIDOAuthClient(url=url, access_token="access_token")
            with pytest.raises(
                    ServiceError, match="Error fetching data from ORCID Auth api"
            ):
                client.revoke_token()


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


def test_ORCIDAPI_get_profile():
    with no_stderr():
        with mock_orcid_api_service() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            profile = client.get_profile(orcid_id)
            assert isinstance(profile, orcid_api.ORCIDProfile)
            assert profile.orcid_identifier.path == orcid_id


def test_ORCIDAPI_get_works():
    with no_stderr():
        with mock_orcid_api_service() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            works = client.get_works(orcid_id)
            assert isinstance(works, orcid_api.Works)
            assert works.group[0].work_summary[0].put_code == 1487805


def test_ORCIDAPI_get_works_error():
    with no_stderr():
        with mock_orcid_api_service_with_errors() as [_, _, url]:
            orcid_id = "0000-0003-4997-3076"
            client = orcid_api.ORCIDAPIClient(url=url, access_token="access_token")
            with pytest.raises(
                    ServiceError, match="Error fetching data from ORCID Auth api"
            ) as ex:
                client.get_works(orcid_id)


def test_ORCIDAPI_save_work():
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
            work_update = load_test_data("orcid", f"work_{str(put_code)}")
            # don't change anything for now
            result = client.save_work(
                orcid_id, put_code, orcid_api.Work.parse_obj(work_update)
            )
            assert isinstance(result, orcid_api.Work)
            assert result.put_code == put_code


def test_ORCIDAPI_save_work_error():
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
            with pytest.raises(
                    ServiceError, match="Error fetching data from ORCID Auth api"
            ) as ex:
                put_code = 1526002
                work_update = orcid_api.Work.parse_obj(
                    load_test_data("orcid", f"work_{str(put_code)}")
                )
                # don't change anything for now
                client.save_work(orcid_id, put_code, work_update)
            # assert ex.value.error.data["originalResponseJSON"]["response-code"] == 400

            assert ex.value.error.code == "upstreamError"
            assert ex.value.error.title == "Error"
            assert ex.value.error.data.source == "save_work"
            assert ex.value.error.data.status_code == 500
            # assert ex.value.error.response_code == 400
            # assert ex.value.error.data.status_code == 400


def test_make_exception_401():
    # A 401
    ex = httpx.Response(
        status_code=401,
        content=json.dumps(
            {"error": "My Error", "error_description": "Should not see me"}
        ),
    )

    result = orcid_api.make_exception(ex, "foo")
    assert isinstance(result, ServiceError)
    assert result.status_code == 400
    assert result.error.code == "upstreamError"
    assert result.error.title == "Error"
    assert result.error.data.source == "foo"
    assert result.error.data.detail.error == "My Error"
    assert result.error.data.detail.error_description is None
    # assert "error_description" not in result.error.data.detail


def test_make_exception_non_401():
    ex = httpx.Response(
        status_code=400,
        content=json.dumps(
            {
                "response-code": 123,
                "developer-message": "My Developer Message",
                "user-message": "My User Message",
                "error-code": 456,
                "more-info": "My More Info",
            }
        ),
    )

    result = orcid_api.make_exception(ex, "foo")
    assert isinstance(result, ServiceError)
    assert result.status_code == 400
    assert result.error.code == "upstreamError"
    assert result.error.title == "Error"
    assert result.error.data.source == "foo"
    assert result.error.data.detail.response_code == 123
    # assert result.error.data.detail.error_description is None
    # assert "error_description" not in result.error.data.detail


def test_make_exception_internal_server():
    ex = httpx.Response(
        status_code=500,
        content=json.dumps(
            {
                "message-version": "123",
                "orcid-profile": None,
                "orcid-search-results": None,
                "error-desc": {"value": "My error desc"},
            }
        ),
    )

    result = orcid_api.make_exception(ex, "foo")
    assert isinstance(result, ServiceError)
    assert result.status_code == 400
    assert result.error.code == "upstreamError"
    assert result.error.title == "Error"
    assert result.error.data.source == "foo"
    assert result.error.data.detail.message_version == "123"
    # assert result.error.data.detail.error_description is None
    # assert "error_description" not in result.error.data.detail
