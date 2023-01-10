import contextlib
import json

import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from test.mocks.mock_contexts import mock_auth_service, mock_orcid_api_service, no_stderr


@pytest.fixture
def fake_fs(fs):
    fake_config = """
kbase:
  services:
    Auth2:
      url: http://127.0.0.1:9999/services/auth/api/V2/token
      tokenCacheLifetime: 300000
      tokenCacheMaxSize: 20000
    ServiceWizard:
      url: http://127.0.0.1:9999/services/service_wizard
  uiOrigin: https://ci.kbase.us
  defaults:
    serviceRequestTimeout: 500
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

    fake_index = """
    {
    "last_id": 9,
    "entities": {
        "foo": {
            "id": 9,
            "metadata": {},
            "events": [
                {
                    "event": "created",
                    "at": "2022-12-02T01:13:36.533017+00:00"
                }
            ]
        }
    }
}
    """
    fs.create_file("/kb/module/work/data/users/index.json", contents=fake_index)

    fake_link_record = """
    {
    "orcid_auth": {
        "access_token": "1eef6e01-62be-467c-b140-973011ef0cb7",
        "token_type": "bearer",
        "refresh_token": "0111ac66-c9a8-42ef-9e71-109ae091b8df",
        "expires_in": 631138518,
        "scope": "/read-limited openid /activities/update",
        "name": "Erik Pearson",
        "orcid": "0000-0003-4997-3076",
        "id_token": "eyJraWQiOiJzYW5kYm94LW9yY2lkLW9yZy0zaHBnb3NsM2I2bGFwZW5oMWV3c2dkb2IzZmF3ZXBvaiIsImFsZyI6IlJTMjU2In0.eyJhdF9oYXNoIjoiRGsyR01qZ1FTdVYwZFJ5SUZMYmd3dyIsImF1ZCI6IkFQUC1SQzNQTTNLU01NVjNHS1dTIiwic3ViIjoiMDAwMC0wMDAzLTQ5OTctMzA3NiIsImF1dGhfdGltZSI6MTY2OTk0MzYxMiwiYW1yIjoicHdkIiwiaXNzIjoiaHR0cHM6XC9cL3NhbmRib3gub3JjaWQub3JnIiwiZXhwIjoxNjcwMDMwMDE0LCJnaXZlbl9uYW1lIjoiRXJpayIsImlhdCI6MTY2OTk0MzYxNCwiZmFtaWx5X25hbWUiOiJQZWFyc29uIiwianRpIjoiMjU3Y2U3MjItMzZhYS00ZjJjLTllN2YtMDJlZWEzZGIzZDk2In0.mMIWYtPCq52YQYugff57tejpZhnL_8J9_eARgd-niVHtA-lFnrVGaoL-oVzr5gqjWFvCuAyZU78pKxFaSczcwDViW2UeBmgFjFyj0hokmoXc6iH51XQUc_X3hwCod67oY8dyMPMy_awAIgUQ3ZK3Se64Pd1_odoLZi4O7oSba5dMnQ2tD0s-57BcPfittp6vqXVGE00K1M-qyrR72Lmj6ML2xfORPfUOZW6M3zLyX_ipBE36tQk1cjQhveNwUgDFlsiA1p6V1s1L7vpIiNpB1y9lOmUZQJICnusKMQ35EHPtS7saybwvXH7EwqwN9kvMfEOekbwHgYvsPrAbHHh06g"
    },
    "created_at": 1669943616532,
    "expires_at": 2301082134532
}
    """
    fs.create_file("/kb/module/work/data/users/9.json", contents=fake_link_record)

    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            with mock_orcid_api_service():
                yield


def test_get_work(fake_fs):
    with mock_services():
        put_code = 1526002
        client = TestClient(app)
        response = client.get(f"/works/{put_code}",
                              headers={"Authorization": "foo"}
                              )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work['putCode'] == '1526002'


def test_get_work_errors(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # An unlinked user gets a 404 from us.
        #
        response = client.get(f"/works/bar",
                              headers={"Authorization": "bar"}
                              )
        assert response.status_code == 404

        #
        # An api misuse which penetrates the call; ideally
        # there should not be anything like this.
        # In this case, the mock orcid server is set up
        # to return a 200 text response for the "bar" putCode, which
        # triggers a parse error.
        #
        response = client.get(f"/works/bar",
                              headers={"Authorization": "foo"}
                              )
        assert response.status_code == 400

        #
        # A bad put code results in a 400 from ORCID
        #
        response = client.get(f"/works/foo",
                              headers={"Authorization": "foo"}
                              )
        assert response.status_code == 400
        error = response.json()
        assert error['data']['originalStatusCode'] == 400
        assert error['data']['originalResponseJSON']['error-code'] == 9006


def test_get_works(fake_fs):
    with mock_services():
        client = TestClient(app)
        response = client.get(f"/works",
                              headers={"Authorization": "foo"}
                              )
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
        response = client.get(f"/works",
                              headers={"Authorization": "bar"}
                              )
        assert response.status_code == 404

        #
        # An api misuse which penetrates the call; ideally
        # there should not be anything like this.
        # In this case, the mock orcid server is set up
        # to return a 200 text response for the "bar" putCode, which
        # triggers a parse error.
        #
        # response = client.get(f"/works",
        #                       headers={"Authorization": "foo"}
        #                       )
        # assert response.status_code == 400


# TODO: left off here, copied from test_get_work - added work_1526002_normalized.json to
# serve as a basis for input work records - will need to copy that and perhaps modify slightly for
# put_work.
def test_create_work(fake_fs):
    with mock_services():
        # Note that we do not need to launch a mock server here,
        # though we might want to later as that really tests the API
        # front to back.
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
                    "relationship": "self"
                }
            ]
        }
        response = client.post(f"/works",
                               headers={"Authorization": "foo"},
                               content=json.dumps(new_work_data)
                               )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work['putCode'] == '1526002'


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
                    "relationship": "self"
                }
            ]
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
        response = client.post(f"/works",
                               headers={"Authorization": "bar"},
                               content=json.dumps(new_work_data)
                               )
        assert response.status_code == 404

        # Error: exception saving work record to orcid; i.e.
        # thrown by the http call.
        new_work_data['title'] = "trigger-http-exception"
        response = client.post(f"/works",
                               headers={"Authorization": "foo"},
                               content=json.dumps(new_work_data)
                               )
        assert response.status_code == 400

        # Error: 500 returned from orcid
        # Invoke this with a special put code
        new_work_data['title'] = "trigger-500"
        response = client.post(f"/works",
                               headers={"Authorization": "foo"},
                               content=json.dumps(new_work_data)
                               )
        assert response.status_code == 500
        # assert response.text == "AN ERROR"

        # Error: Any other non-200 returned from orcid
        new_work_data['title'] = "trigger-400"
        response = client.post(f"/works",
                               headers={"Authorization": "foo"},
                               content=json.dumps(new_work_data)
                               )
        assert response.status_code == 400


def test_save_work(fake_fs):
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
                    "relationship": "self"
                },
                # adds an extra one
                # TODO: should model differnt relationship
                # TODO: what about mimicking errors in the
                # api like a duplicate "self" relationship?
                {
                    "type": "doi",
                    "value": "1234",
                    "url": "https://example.com",
                    "relationship": "self"
                }
            ]
        }
        response = client.put(f"/works",
                              headers={"Authorization": "foo"},
                              content=json.dumps(new_work_data)
                              )
        assert response.status_code == 200
        work = response.json()
        assert isinstance(work, dict)
        assert work['putCode'] == '1526002'


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
                    "relationship": "self"
                }
            ]
        }
        response = client.put(f"/works",
                              headers={"Authorization": "bar"},
                              content=json.dumps(new_work_data)
                              )
        assert response.status_code == 404


def test_delete_work(fake_fs):
    with mock_services():
        put_code = 1526002
        client = TestClient(app)
        response = client.delete(f"/works/{put_code}",
                                 headers={"Authorization": "foo"}
                                 )
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, dict)
        assert result['ok'] is True
