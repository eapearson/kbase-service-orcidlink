import contextlib

import pytest
from fastapi.testclient import TestClient
from orcidlink.lib import utils
from orcidlink.lib.config import Config2
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import generate_kbase_token
import os
from unittest import mock

client = TestClient(app)


TEST_LINK = load_data_json("link1.json")
TEST_LINK_BAR = load_data_json("link-bar.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


async def create_link(link_record):
    sm = storage_model.storage_model()
    await sm.db.links.drop()
    await sm.create_link_record(LinkRecord.model_validate(link_record))


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
