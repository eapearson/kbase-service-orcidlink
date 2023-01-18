import contextlib
import json

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.routers.works import parse_date
from orcidlink.storage import storage_model
from test.data.utils import load_data_file, load_data_json
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.toml", contents=config_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
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
        response = client.get(f"/works/{put_code}", headers={"Authorization": "foo"})
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == "1526002"


def test_get_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get(f"/works/bar", headers={"Authorization": "bar"})
        assert response.status_code == 422

        #
        # An unlinked user gets a 422, since fastapi validates the url param
        # and it should be int.
        #
        response = client.get(f"/works/1526002", headers={"Authorization": "bar"})
        assert response.status_code == 404

        #
        # An api misuse which penetrates the call; ideally
        # there should not be anything like this.
        # In this case, the mock orcid server is set up
        # to return a 200 text response for the "123" putCode, which
        # triggers a parse error.
        #
        response = client.get(f"/works/123", headers={"Authorization": "foo"})
        assert response.status_code == 400

        #
        # A bad put code results in a 400 from ORCID
        #
        response = client.get(f"/works/456", headers={"Authorization": "foo"})
        assert response.status_code == 400
        error = response.json()
        assert error["data"]["originalStatusCode"] == 400
        assert error["data"]["originalResponseJSON"]["error-code"] == 9006


def test_get_works(fake_fs):
    with mock_services():
        create_link()
        client = TestClient(app)
        response = client.get(f"/works", headers={"Authorization": "foo"})
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
        response = client.get(f"/works", headers={"Authorization": "bar"})
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
            "putCode": "1526002",
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
            "/works",
            headers={"Authorization": "foo"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == "1526002"


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
        # client.headers['authorization'] = 'foo'
        # response = client.post(f"/works",
        #                        headers={"Authorization": "foo"},
        #                        content=json.dumps(new_work_data)
        #                        )
        # assert response.status_code == 200
        # work = response.json()
        # assert isinstance(work, dict)
        # assert work['putCode'] == '1526002'

        # Error: link_record not found
        # client.headers['authorization'] = 'bar'
        response = client.post(
            f"/works",
            headers={"Authorization": "bar"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404

        # Error: exception saving work record to orcid; i.e.
        # thrown by the http call.
        new_work_data["title"] = "trigger-http-exception"
        response = client.post(
            f"/works",
            headers={"Authorization": "foo"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 400

        # Error: 500 returned from orcid
        # Invoke this with a special put code
        new_work_data["title"] = "trigger-500"
        response = client.post(
            f"/works",
            headers={"Authorization": "foo"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 500
        # assert response.text == "AN ERROR"

        # Error: Any other non-200 returned from orcid
        new_work_data["title"] = "trigger-400"
        response = client.post(
            f"/works",
            headers={"Authorization": "foo"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 400


def test_save_work(fake_fs):
    with mock_services():
        create_link()

        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": "1526002",
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
                # TODO: should model differnt relationship
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
            f"/works",
            headers={"Authorization": "foo"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work["putCode"] == "1526002"


def test_save_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        # TODO: get from file.
        new_work_data = {
            "putCode": "1526002",
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
            f"/works",
            headers={"Authorization": "bar"},
            content=json.dumps(new_work_data),
        )
        assert response.status_code == 404


def test_delete_work(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(f"/works/{put_code}", headers={"Authorization": "foo"})
        assert response.status_code == 204


def test_delete_work_bad_no_link(fake_fs):
    with mock_services():
        create_link()
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(f"/works/{put_code}", headers={"Authorization": "bar"})
        assert response.status_code == 404


def test_delete_work_not_source(fake_fs):
    with mock_services():
        create_link()
        # Use a put code not in the mock service, in this case we
        # transpose the final 2 with 3.
        client = TestClient(app)
        put_code = 123
        response = client.delete(f"/works/{put_code}", headers={"Authorization": "foo"})
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
        response = client.delete(f"/works/{put_code}", headers={"Authorization": "foo"})
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


def test_parse_date():
    assert parse_date("2000") == {"year": {"value": "2000"}}
    assert parse_date("2000/1") == {"year": {"value": "2000"}, "month": {"value": "01"}}
    assert parse_date("2000/12") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
    }
    assert parse_date("2000/1/2") == {
        "year": {"value": "2000"},
        "month": {"value": "01"},
        "day": {"value": "02"},
    }
    assert parse_date("2000/12/3") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
        "day": {"value": "03"},
    }
    assert parse_date("2000/12/34") == {
        "year": {"value": "2000"},
        "month": {"value": "12"},
        "day": {"value": "34"},
    }
