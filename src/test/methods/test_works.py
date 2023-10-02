import contextlib
import os
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_API_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_api_service,
    no_stderr,
)
from test.mocks.testing_utils import (
    TOKEN_BAR,
    TOKEN_FOO,
    assert_json_rpc_error,
    assert_json_rpc_result_ignore_result,
    rpc_call,
)
from unittest import mock

import pytest

from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model


@pytest.fixture
def fake_fs(fs):
    data_dir = os.environ["TEST_DATA_DIR"]
    fs.add_real_directory(data_dir)
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
    },
    "created_at": 1669943616532,
    "expires_at": 2301082134532,
    "retires_at": 2301082134532,
    "username": "foo",
}


async def create_link():
    sm = storage_model.storage_model()
    await sm.db.links.drop()
    await sm.create_link_record(LinkRecord.model_validate(TEST_LINK))


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            with mock_orcid_api_service(MOCK_ORCID_API_PORT):
                yield


async def test_get_work(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            put_code = 1526002
            params = {"username": "foo", "put_code": put_code}
            response = rpc_call("get-work", params, TOKEN_FOO)
            result = assert_json_rpc_result_ignore_result(response)
            assert result["work"]["putCode"] == put_code


async def test_get_work2(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            put_code = 1487805
            params = {"username": "foo", "put_code": put_code}
            response = rpc_call("get-work", params, TOKEN_FOO)
            result = assert_json_rpc_result_ignore_result(response)
            assert result["work"]["putCode"] == put_code


async def test_get_work_errors(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            #
            # Omitting a param
            # TODO: do we really need to test this?
            #
            params = {
                "username": "bar",
            }
            response = rpc_call("get-work", params, TOKEN_BAR)
            assert_json_rpc_error(response, -32602, "Invalid params")

            #
            # An unlinked user gets a 422, since fastapi validates the url param
            # and it should be int.
            #
            params = {"username": "bar", "put_code": 1526002}
            response = rpc_call("get-work", params, TOKEN_BAR)
            assert_json_rpc_error(response, 1020, "Not Found")

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
            await create_link()
            params = {"username": "foo", "put_code": 123}
            response = rpc_call("get-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1041, "Received Incorrect Content Type")
            #
            # A bad put code results in a 400 from ORCID
            #
            params = {"username": "foo", "put_code": 456}
            response = rpc_call("get-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")


async def test_get_works(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            params = {
                "username": "foo",
            }
            response = rpc_call("get-works", params, TOKEN_FOO)
            result = assert_json_rpc_result_ignore_result(response)
            assert isinstance(result, list)
            # assert work['putCode'] == '1526002'


def test_get_works_errors(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            params = {
                "username": "bar",
            }
            response = rpc_call("get-works", params, TOKEN_BAR)
            assert_json_rpc_error(response, 1020, "Not Found")


# TODO: left off here, copied from test_get_work - added work_1526002_normalized.json to
# serve as a basis for input work records - will need to copy that and perhaps modify
# slightly for put_work.
async def test_create_work(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()

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
                "citation": {
                    "type": "formatted-vancouver",
                    "value": "my reference here",
                },
                "shortDescription": "my short description",
                "selfContributor": {
                    "orcidId": "1111-2222-3333-4444",
                    "name": "Bar Baz",
                    "roles": [],
                },
                "otherContributors": [],
            }

            params = {"username": "foo", "new_work": new_work_data}
            response = rpc_call("create-work", params, TOKEN_FOO)
            result = assert_json_rpc_result_ignore_result(response)
            assert result["work"]["putCode"] == 1526002


async def test_create_work_errors(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            # Note that we do not need to launch a mock server here,
            # though we might want to later as that really tests the API
            # front to back.
            await create_link()

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
                "citation": {
                    "type": "formatted-vancouver",
                    "value": "my reference here",
                },
                "shortDescription": "my short description",
                "doi": "123",
                "selfContributor": {
                    "orcidId": "1111-2222-3333-4444",
                    "name": "Bar Baz",
                    "roles": [],
                },
                "otherContributors": [],
            }

            params = {"username": "bar", "new_work": new_work_data}
            response = rpc_call("create-work", params, TOKEN_BAR)
            assert_json_rpc_error(response, 1020, "Not Found")

            # Error: exception saving work record to orcid; i.e.
            # thrown by the http call.
            new_work_data["title"] = "trigger-http-exception"
            params = {"username": "foo", "new_work": new_work_data}
            response = rpc_call("create-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")

            # Error: 500 returned from orcid
            # Invoke this with a special put code
            new_work_data["title"] = "trigger-500"
            params = {"username": "foo", "new_work": new_work_data}
            response = rpc_call("create-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")

            # Error: Any other non-200 returned from orcid
            new_work_data["title"] = "trigger-400"
            params = {"username": "foo", "new_work": new_work_data}
            response = rpc_call("create-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")


# def test_external_id():
#     with mock.patch.dict(os.environ, TEST_ENV, clear=True):
#         external_id = orcid_api.ExternalId(
#             external_id_type="foo",
#             external_id_value="value",
#             external_id_normalized=None,
#             external_id_url=orcid_api.ORCIDStringValue(value="url"),
#             external_id_relationship="rel",
#         )
# orcid_api.ORCIDExternalId.model_validate({
#     "external-id-type": "foo",
#     "external-id-value": "value",
#     "external-id-normalized": None,
#     "external-id-url": {
#         "value": "url"
#     },
#     "external-id-relationship": "rel"
# })


async def test_save_work(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()

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
                "citation": {
                    "type": "formatted-vancouver",
                    "value": "my reference here",
                },
                "shortDescription": "my short description",
                "doi": "123",
                "selfContributor": {
                    "orcidId": "1111-2222-3333-4444",
                    "name": "Bar Baz",
                    "roles": [],
                },
                "otherContributors": [],
            }
            params = {"username": "foo", "work_update": new_work_data}
            response = rpc_call("update-work", params, TOKEN_FOO)
            result = assert_json_rpc_result_ignore_result(response)
            assert result["work"]["putCode"] == 1526002
            # response = client.put(
            #     "/orcid/works",
            #     headers={"Authorization": TOKEN_FOO},
            #     content=json.dumps(new_work_data),
            # )
            # assert response.status_code == 200
            # work = response.json()
            # assert isinstance(work, dict)
            # assert work["putCode"] == 1526002


def test_save_work_errors(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
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
                "citation": {
                    "type": "formatted-vancouver",
                    "value": "my reference here",
                },
                "shortDescription": "my short description",
                "doi": "123",
                "selfContributor": {
                    "orcidId": "1111-2222-3333-4444",
                    "name": "Bar Baz",
                    "roles": [],
                },
                "otherContributors": [],
            }
            params = {"username": "bar", "work_update": new_work_data}
            response = rpc_call("update-work", params, TOKEN_BAR)
            assert_json_rpc_error(response, 1020, "Not Found")

            # response = client.put(
            #     "/orcid/works",
            #     headers={"Authorization": TOKEN_BAR},
            #     content=json.dumps(new_work_data),
            # )
            # assert response.status_code == 404


async def test_delete_work(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            put_code = 1526002
            params = {"username": "foo", "put_code": put_code}
            response = rpc_call("delete-work", params, TOKEN_FOO)

            result = assert_json_rpc_result_ignore_result(response)
            assert result is None


async def test_delete_work_bad_no_link(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            put_code = 1526002
            params = {"username": "bar", "put_code": put_code}
            response = rpc_call("delete-work", params, TOKEN_BAR)
            assert_json_rpc_error(response, 1020, "Not Found")


async def test_delete_work_not_source(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            # Use a put code not in the mock service, in this case we
            # transpose the final 2 with 3.
            put_code = 123

            params = {"username": "foo", "put_code": put_code}
            response = rpc_call("delete-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")


async def test_delete_work_put_code_not_found(fake_fs):
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link()
            # Use a put code not in the mock service, in this case we
            # transpose the final 2 with 3.
            put_code = 456

            params = {"username": "foo", "put_code": put_code}
            response = rpc_call("delete-work", params, TOKEN_FOO)
            assert_json_rpc_error(response, 1050, "Upstream Error")
