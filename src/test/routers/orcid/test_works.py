import contextlib
import json

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.service_clients import orcid_api
from orcidlink.storage import storage_model
from test.mocks.data import load_data_file, load_data_json
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)
from test.mocks.testing_utils import TOKEN_BAR, TOKEN_FOO

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/deploy/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/test/data")
    yield fs


TEST_LINK = load_data_json("link1.json")

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
    sm.create_link_record(LinkRecord.parse_obj(TEST_LINK))


@contextlib.contextmanager
def mock_services():
    # config(True)
    with no_stderr():
        with mock_auth_service():
            with mock_orcid_api_service():
                yield


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


def test_get_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get(f"/orcid/works/bar", headers={"Authorization": TOKEN_BAR})
        assert response.status_code == 422

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get(
            f"/orcid/works/1526002", headers={"Authorization": TOKEN_BAR}
        )
        assert response.status_code == 404

        #
        # An api misuse which penetrates the call; ideally
        # there should not be anything like this.
        # In this case, the mock orcid server is set up
        # to return a 200 text response for the "123" putCode, which
        # triggers a parse error.
        #
        response = client.get(f"/orcid/works/123", headers={"Authorization": TOKEN_FOO})
        assert response.status_code == 400

        #
        # A bad put code results in a 400 from ORCID
        #
        response = client.get(f"/orcid/works/456", headers={"Authorization": TOKEN_FOO})
        assert response.status_code == 400
        error = response.json()
        expected = {
            "code": "upstreamError",
            "title": "Error",
            "message": "Error fetching data from ORCID Auth api",
            "data": {
                "source": "get_work",
                "status_code": 400,
                "detail": {
                    "response-code": 400,
                    "developer-message": 'The client application sent a bad request to ORCID. Full validation error: For input string: "1526002x"',
                    "user-message": "The client application sent a bad request to ORCID.",
                    "error-code": 9006,
                    "more-info": "https://members.orcid.org/api/resources/troubleshooting",
                },
            },
        }
        assert error == expected


def test_get_works(fake_fs):
    with mock_services():
        create_link()
        client = TestClient(app)
        response = client.get(f"/orcid/works", headers={"Authorization": TOKEN_FOO})
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, list)
        # assert work['putCode'] == '1526002'


def test_get_works_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 404 from us.
        #
        response = client.get(f"/orcid/works", headers={"Authorization": TOKEN_BAR})
        assert response.status_code == 404


# TODO: left off here, copied from test_get_work - added work_1526002_normalized.json to
# serve as a basis for input work records - will need to copy that and perhaps modify slightly for
# put_work.
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
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                }
            ],
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


def test_create_work_errors(fake_fs):
    with mock_services():
        # Note that we do not need to launch a mock server here,
        # though we might want to later as that really tests the API
        # front to back.
        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "workType": "online-resource",
            "title": "Some Data Set, yo, bro, whoa",
            "journal": "Me myself and I and me",
            "date": "2021",
            "url": "https://kbase.us",
            "externalIds": [
                {
                    "type": "doi",
                    "value": "123",
                    "url": "https://example.com",
                    "relationship": "self",
                }
            ],
        }

        # Error: link_record not found
        response = client.post(
            f"/orcid/works",
            headers={"Authorization": TOKEN_BAR},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404

        # Error: exception saving work record to orcid; i.e.
        # thrown by the http call.
        new_work_data["title"] = "trigger-http-exception"
        response = client.post(
            f"/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 400

        # Error: 500 returned from orcid
        # Invoke this with a special put code
        new_work_data["title"] = "trigger-500"
        response = client.post(
            f"/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 500
        # assert response.text == "AN ERROR"

        # Error: Any other non-200 returned from orcid
        new_work_data["title"] = "trigger-400"
        response = client.post(
            f"/orcid/works",
            headers={"Authorization": TOKEN_FOO},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 400


def test_external_id():
    external_id = orcid_api.ORCIDExternalId(
        external_id_type="foo",
        external_id_value="value",
        external_id_normalized=None,
        external_id_url=orcid_api.StringValue(value="url"),
        external_id_relationship="rel",
    )
    # orcid_api.ORCIDExternalId.parse_obj({
    #     "external-id-type": "foo",
    #     "external-id-value": "value",
    #     "external-id-normalized": None,
    #     "external-id-url": {
    #         "value": "url"
    #     },
    #     "external-id-relationship": "rel"
    # })


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
        }
        response = client.put(
            f"/orcid/works",
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
        }
        response = client.put(
            f"/orcid/works",
            headers={"Authorization": TOKEN_BAR},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404


def test_delete_work(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_FOO}
        )
        assert response.status_code == 204


def test_delete_work_bad_no_link(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(
            f"/orcid/works/{put_code}", headers={"Authorization": TOKEN_BAR}
        )
        assert response.status_code == 404


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
        assert response.status_code == 400
        result = response.json()
        assert isinstance(result, dict)
        assert result["code"] == "orcid-api-error"
        assert result["title"] == "ORCID API Error"
        assert (
                result["message"]
                == "The ORCID API reported an error fo this request, see 'data' for cause"
        )
        assert result["data"]["response-code"] == 403
        assert result["data"]["error-code"] == 9010
        # # Tha actual messages may change over time, and are not used
        # # programmatically


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
        assert response.status_code == 400
        result = response.json()
        assert isinstance(result, dict)
        assert result["code"] == "orcid-api-error"
        assert result["title"] == "ORCID API Error"
        assert (
                result["message"]
                == "The ORCID API reported an error fo this request, see 'data' for cause"
        )
        assert result["data"]["response-code"] == 404
        assert result["data"]["error-code"] == 9016
        # # Tha actual messages may change over time, and are not used
        # # programmatically
