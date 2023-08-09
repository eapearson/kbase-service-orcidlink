import contextlib
import json
from test.mocks.data import load_data_file
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)
from test.mocks.testing_utils import TOKEN_BAR, TOKEN_FOO

import aiohttp
import pytest
from fastapi.testclient import TestClient

from orcidlink.lib import utils
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.lib.service_clients import orcid_api
from orcidlink.storage import storage_model
import os
from unittest import mock


@pytest.fixture
def fake_fs(fs):
    fs.add_real_directory(utils.module_path("test/data"))
    yield fs


# TEST_LINK = load_data_json("link1.json")

TEST_LINK = {
    "orcid_auth": {
        "access_token": "access-token",
        "token_type": "bearer",
        "refresh_token": "refresh-token",
        "expires_in": 631138518,
        "scope": "/read-limited openid /activities/update",
        "name": "Foo bar",
        "orcid": "0000-0003-4997-3076",
        "id_token": "id-token",
    },
    "created_at": 1669943616532,
    "expires_at": 2301082134532,
    "username": "foo",
}


def create_link():
    sm = storage_model.storage_model()
    sm.db.links.drop()
    sm.create_link_record(LinkRecord.model_validate(TEST_LINK))

MOCK_AUTH_PORT = 9999
MOCK_ORCID_API_PORT = 9998


@contextlib.contextmanager
def mock_services():
    # config(True)
    with no_stderr():
        with mock_auth_service(MOCK_AUTH_PORT):
            with mock_orcid_api_service(MOCK_ORCID_API_PORT):
                yield


TEST_ENV = {
    "KBASE_ENDPOINT": f"http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "MONGO_HOST": "mongo",
    "MONGO_PORT": "27017",
    "MONGO_DATABASE": "orcidlink",
    "MONGO_USERNAME": "dev",
    "MONGO_PASSWORD": "d3v",
    "ORCID_API_BASE_URL": "http://127.0.0.1:9998",
    "ORCID_OAUTH_BASE_URL": ""
}

@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_work(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.get(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == 1526002


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_work2(fake_fs):
    with mock_services():
        create_link()
        put_code = 1487805
        client = TestClient(app)
        response = client.get(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == 1487805


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get("/orcid/works/bar", headers={"Authorization": TOKEN_BAR})
        assert response.status_code == 422

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get(
            "/orcid/works/1526002", headers={"Authorization": TOKEN_BAR}
        )
        assert response.status_code == 404

        #
        # An api misuse which penetrates the call; ideally
        # there should not be anything like this.
        # In this case, the mock orcid server is set up
        # to return a 200 text response for the "123" putCode, which
        # triggers a parse error.
        #
        # TODO: this is rather terrible - the test client does not call the
        # endpoint in the same way as calling the running server. Specifically,
        # the middleware is not run, including that which catches all exceptions
        # calls custom exception handlers. So we can't actually test the
        # respose here. I think we'll need integration tests for that.
        #
        # Or perhaps we should just catch all exceptions w/in the endpoint
        # handlers and always return a response.
        try:
            response = client.get(
                "/orcid/works/123", headers={"Authorization": TOKEN_FOO}
            )
        except aiohttp.ContentTypeError as cte:
            # assert response.status_code == 502
            # error = response.json()
            # assert error["code"] == "upstreamError"
            assert (
                cte.message
                == "Attempt to decode JSON with unexpected mimetype: text/plain"
            )

        #
        # A bad put code results in a 400 from ORCID
        #
        response = client.get("/orcid/works/456", headers={"Authorization": TOKEN_FOO})
        assert response.status_code == 502
        error = response.json()
        assert error["code"] == "upstreamError"
        assert error["message"] == "Error fetching data from ORCID"
        # print('OH really', type(error), error)
        # expected = {
        #     "code": "upstreamError",
        #     "title": "Error",
        #     "message": "Error fetching data from ORCID Auth api",
        #     "data": {
        #         "source": "get_work",
        #         "status_code": 400,
        #         "detail": {
        #             "response-code": 400,
        #             "developer-message": 'The client application sent a bad request to ORCID. Full validation error: For input string: "1526002x"',
        #             "user-message": "The client application sent a bad request to ORCID.",
        #             "error-code": 9006,
        #             "more-info": "https://members.orcid.org/api/resources/troubleshooting",
        #         },
        #     },
        # }
        # assert error == expected


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_works(fake_fs):
    with mock_services():
        create_link()
        client = TestClient(app)
        response = client.get("/orcid/works", headers={"Authorization": TOKEN_FOO})
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, list)
        # assert work['putCode'] == '1526002'


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_works_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 404 from us.
        #
        response = client.get("/orcid/works", headers={"Authorization": TOKEN_BAR})
        assert response.status_code == 404


# TODO: left off here, copied from test_get_work - added work_1526002_normalized.json to
# serve as a basis for input work records - will need to copy that and perhaps modify slightly for
# put_work.
@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_create_work(fake_fs):
    with mock_services():
        create_link()

        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": 1526002,
            "createdAt": 1663706262725,
            "updatedAt": 1671119638386,
            "source": "KBase CI",
            "title": "Some Data Set, yo, bro, whoa",
            "journal": "Me myself and I and me",
            "date": "2021",
            "workType": "online-resource",
            "url": "https://kbase.us",
            "doi": "123",
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                }
            ],
            "citation": {"type": "formatted-vancouver", "value": "my reference here"},
            "shortDescription": "my short description",
            "selfContributor": {
                "orcidId": "1111-2222-3333-4444",
                "name": "Bar Baz",
                "roles": [],
            },
            "otherContributors": [],
        }
        response = client.post(
            "/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == 1526002


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_create_work_errors(fake_fs):
    with mock_services():
        # Note that we do not need to launch a mock server here,
        # though we might want to later as that really tests the API
        # front to back.
        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": 1526002,
            "createdAt": 1663706262725,
            "updatedAt": 1671119638386,
            "source": "KBase CI",
            "title": "Some Data Set, yo, bro, whoa",
            "journal": "Me myself and I and me",
            "date": "2021",
            "workType": "online-resource",
            "url": "https://kbase.us",
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                }
            ],
            "citation": {"type": "formatted-vancouver", "value": "my reference here"},
            "shortDescription": "my short description",
            "doi": "123",
            "selfContributor": {
                "orcidId": "1111-2222-3333-4444",
                "name": "Bar Baz",
                "roles": [],
            },
            "otherContributors": [],
        }

        # Error: link_record not found
        response = client.post(
            "/orcid/works",
            headers={"Authorization": TOKEN_BAR},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404

        # Error: exception saving work record to orcid; i.e.
        # thrown by the http call.
        new_work_data["title"] = "trigger-http-exception"
        response = client.post(
            "/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 502

        # Error: 500 returned from orcid
        # Invoke this with a special put code
        new_work_data["title"] = "trigger-500"
        response = client.post(
            "/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 502
        # assert response.text == "AN ERROR"

        # Error: Any other non-200 returned from orcid
        new_work_data["title"] = "trigger-400"
        response = client.post(
            "/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 502


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_external_id():
    external_id = orcid_api.ExternalId(
        external_id_type="foo",
        external_id_value="value",
        external_id_normalized=None,
        external_id_url=orcid_api.StringValue(value="url"),
        external_id_relationship="rel",
    )
    # orcid_api.ORCIDExternalId.model_validate({
    #     "external-id-type": "foo",
    #     "external-id-value": "value",
    #     "external-id-normalized": None,
    #     "external-id-url": {
    #         "value": "url"
    #     },
    #     "external-id-relationship": "rel"
    # })


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_save_work(fake_fs):
    with mock_services():
        create_link()

        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": 1526002,
            "title": "Some Data Set, yo, bro, whoa",
            "journal": "Me myself and I and me",
            "date": "2021",
            "workType": "online-resource",
            "url": "https://kbase.us",
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                },
                # adds an extra one
                # TODO: should model different relationship
                # TODO: what about mimicking errors in the
                # api like a duplicate "self" relationship?
                {
                    "type": "doi",
                    "value": "1234",
                    "url": "https://example.com",
                    "relationship": "self",
                },
            ],
            "citation": {"type": "formatted-vancouver", "value": "my reference here"},
            "shortDescription": "my short description",
            "doi": "123",
            "selfContributor": {
                "orcidId": "1111-2222-3333-4444",
                "name": "Bar Baz",
                "roles": [],
            },
            "otherContributors": [],
        }
        response = client.put(
            "/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == 1526002


def test_save_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": 1526002,
            "title": "Some Data Set, yo, bro, whoa",
            "journal": "Me myself and I and me",
            "date": "2021",
            "workType": "online-resource",
            "url": "https://kbase.us",
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                }
            ],
            "citation": {"type": "formatted-vancouver", "value": "my reference here"},
            "shortDescription": "my short description",
            "doi": "123",
            "selfContributor": {
                "orcidId": "1111-2222-3333-4444",
                "name": "Bar Baz",
                "roles": [],
            },
            "otherContributors": [],
        }
        response = client.put(
            "/orcid/works",
            headers={"Authorization": TOKEN_BAR},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_delete_work(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 204


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_delete_work_bad_no_link(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_BAR}
        )
        assert response.status_code == 404


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_delete_work_not_source(fake_fs):
    with mock_services():
        create_link()
        # Use a put code not in the mock service, in this case we
        # transpose the final 2 with 3.
        client = TestClient(app)
        put_code = 123
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 502
        result = response.json()
        assert result["code"] == "upstreamError"
        assert result["title"] == "Upstream Error"
        # assert (
        #         result["message"]
        #         == "The ORCID API reported an error fo this request, see 'data' for cause"
        # )
        # assert result["data"]["response-code"] == 403
        # assert result["data"]["error-code"] == 9010
        # # Tha actual messages may change over time, and are not used
        # # programmatically


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_delete_work_put_code_not_found(fake_fs):
    with mock_services():
        create_link()
        # Use a put code not in the mock service, in this case we
        # transpose the final 2 with 3.
        client = TestClient(app)
        put_code = 456
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 502
        result = response.json()
        assert result["code"] == "upstreamError"
        assert result["title"] == "Upstream Error"
        # assert (
        #         result["message"]
        #         == "The ORCID API reported an error fo this request, see 'data' for cause"
        # )
        # assert result["data"]["response-code"] == 404
        # assert result["data"]["error-code"] == 9016
        # # Tha actual messages may change over time, and are not used
        # # programmatically
