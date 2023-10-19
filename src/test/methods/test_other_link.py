import contextlib
import os
from test.mocks.data import load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, TEST_ENV
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from test.mocks.testing_utils import (
    assert_json_rpc_error,
    assert_json_rpc_result,
    clear_database,
    create_link,
    generate_kbase_token,
)
from unittest import mock

from fastapi.testclient import TestClient

from orcidlink.main import app
from orcidlink.model import LinkRecordPublicNonOwner

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


async def test_other_link():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await clear_database()
            await create_link(TEST_LINK_BAR)

            client = TestClient(app)

            rpc = {
                "jsonrpc": "2.0",
                "id": "123",
                "method": "other-link",
                "params": {"username": "bar"},
            }

            response = client.post(
                "/api/v1",
                json=rpc,
                headers={"Authorization": generate_kbase_token("foo")},
            )
            expected = LinkRecordPublicNonOwner.model_validate(
                TEST_LINK_BAR
            ).model_dump()
            assert_json_rpc_result(response, expected)

            response = client.post(
                "/api/v1",
                json=rpc,
                headers={"Authorization": generate_kbase_token("baz")},
            )
            assert_json_rpc_error(response, 1010, "Authorization Required")

            rpc["params"]["username"] = "foo"

            response = client.post(
                "/api/v1",
                json=rpc,
                headers={"Authorization": generate_kbase_token("bar")},
            )
            assert_json_rpc_error(response, 1020, "Not Found")
