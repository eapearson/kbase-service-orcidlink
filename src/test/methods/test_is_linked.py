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
    rpc_call,
)
from unittest import mock

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]
TEST_LINK = load_data_json(TEST_DATA_DIR, "link1.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


#
# Tests
#


async def test_is_linked():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await clear_database()
            params = {"username": "foo"}

            response = rpc_call("is-linked", params, generate_kbase_token("foo"))
            assert_json_rpc_result(response, False)

            await create_link(TEST_LINK)

            response = rpc_call("is-linked", params, generate_kbase_token("foo"))
            assert_json_rpc_result(response, True)


async def test_is_linked_not_authorized():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await clear_database()
            params = {"username": "foo"}

            response = rpc_call("is-linked", params, generate_kbase_token("bar"))
            assert_json_rpc_error(response, 1011, "Not Authorized")
