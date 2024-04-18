import contextlib
import os
from test.mocks.data import load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import (
    assert_json_rpc_error,
    assert_json_rpc_result,
    create_link,
    generate_kbase_token,
)
from unittest import mock

from fastapi.testclient import TestClient

from orcidlink.main import app

client = TestClient(app)

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]

TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")
TEST_LINK_BAR = load_data_json(TEST_DATA_DIR, "link-bar.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


#
# Tests
#


async def test_delete_own_link():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                await create_link(TEST_LINK)

                client = TestClient(app)

                rpc = {
                    "jsonrpc": "2.0",
                    "id": "123",
                    "method": "delete-own-link",
                    "params": {"username": "foo"},
                }

                response = client.post(
                    "/api/v1",
                    json=rpc,
                    headers={"Authorization": generate_kbase_token("foo")},
                )
                assert_json_rpc_result(response, None)

                # And now it should be gone.
                response = client.post(
                    "/api/v1",
                    json=rpc,
                    headers={"Authorization": generate_kbase_token("foo")},
                )
                assert_json_rpc_error(response, 1020, "Not Found")

                # Using a non-existent token should result in auth required
                response = client.post(
                    "/api/v1",
                    json=rpc,
                    headers={"Authorization": generate_kbase_token("baz")},
                )
                assert_json_rpc_error(response, 1010, "Authorization Required")

                # Need to add back a link, so we don't get not-found first.
                await create_link(TEST_LINK)

                # Try it with a different user, should not be authorized
                response = client.post(
                    "/api/v1",
                    json=rpc,
                    headers={"Authorization": generate_kbase_token("bar")},
                )
                assert_json_rpc_error(response, 1011, "Not Authorized")

                rpc["params"]["username"] = "bar"
                response = client.post(
                    "/api/v1",
                    json=rpc,
                    headers={"Authorization": generate_kbase_token("foo")},
                )
                assert_json_rpc_error(response, 1020, "Not Found")
