import contextlib
import os
from test.mocks.data import load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import create_link, generate_kbase_token
from unittest import mock

from fastapi.testclient import TestClient

from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model

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


async def test_get_link():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("foo")}
            )
            assert response.status_code == 200

            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("baz")}
            )
            assert response.status_code == 401

            response = client.get(
                "/link", headers={"Authorization": generate_kbase_token("bar")}
            )
            assert response.status_code == 404

            response = client.get("/link", headers={"Authorization": "bar"})
            assert response.status_code == 422


async def test_get_link_for_orcid():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            orcid_id = TEST_LINK["orcid_auth"]["orcid"]

            client = TestClient(app)
            response = client.get(
                f"/link/for_orcid/{orcid_id}",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response.status_code == 200

            response = client.get(
                f"/link/for_orcid/{orcid_id}",
                headers={"Authorization": generate_kbase_token("baz")},
            )
            assert response.status_code == 401

            response = client.get(
                "/link/for_orcid/not_a_linked_orcid_id",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response.status_code == 404

            response = client.get(
                f"/link/for_orcid/{orcid_id}", headers={"Authorization": "bar"}
            )
            assert response.status_code == 422


async def test_get_link_shared():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK_BAR)

            client = TestClient(app)
            linked_username = "bar"
            linked_username_does_not_exist = "bore"

            response = client.get(
                f"/link/share/{linked_username}",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response.status_code == 200

            response = client.get(
                f"/link/share/{linked_username}",
                headers={"Authorization": generate_kbase_token("baz")},
            )
            assert response.status_code == 401

            response = client.get(
                f"/link/share/{linked_username_does_not_exist}",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            assert response.status_code == 404


async def test_is_linked():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            client = TestClient(app)
            response = client.get(
                "/link/is_linked",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            result = response.json()
            assert result is True

            response = client.get(
                "/link/is_linked",
                headers={"Authorization": generate_kbase_token("bar")},
            )
            result = response.json()
            assert result is False

            response = client.get(
                "/link/is_linked",
                headers={"Authorization": generate_kbase_token("baz")},
            )
            assert response.status_code == 401

            response = client.get("/link/is_linked", headers={"Authorization": "baz"})
            assert response.status_code == 422


async def test_is_orcid_linked():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            await create_link(TEST_LINK)

            orcid_id = TEST_LINK["orcid_auth"]["orcid"]

            client = TestClient(app)
            response = client.get(
                f"/link/is_orcid_linked/{orcid_id}",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            result = response.json()
            assert result is True

            response = client.get(
                "/link/is_orcid_linked/not_a_linked_orcid_id",
                headers={"Authorization": generate_kbase_token("foo")},
            )
            result = response.json()
            assert result is False

            # response = client.get(
            #     f"/link/is_orcid_linked/not_a_linked_orcid_id",
            #     headers={"Authorization": generate_kbase_token("bar")},
            # )
            # result = response.json()
            # assert result is False

            response = client.get(
                f"/link/is_orcid_linked/{orcid_id}",
                headers={"Authorization": generate_kbase_token("baz")},
            )
            assert response.status_code == 401

            response = client.get(
                f"/link/is_orcid_linked/{orcid_id}", headers={"Authorization": "baz"}
            )
            assert response.status_code == 422


async def test_delete_link():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                await create_link(TEST_LINK)

                client = TestClient(app)

                response = client.delete(
                    "/link", headers={"Authorization": generate_kbase_token("foo")}
                )
                assert response.status_code == 204

                response = client.delete(
                    "/link", headers={"Authorization": generate_kbase_token("bar")}
                )
                assert response.status_code == 404

                response = client.delete("/link", headers={"Authorization": "bar"})
                assert response.status_code == 422

                response = client.delete(
                    "/link", headers={"Authorization": generate_kbase_token("baz")}
                )
                assert response.status_code == 401
