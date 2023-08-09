import contextlib

import pytest
from fastapi.testclient import TestClient
from orcidlink.lib import utils
from orcidlink.lib.config import Config2
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model
from test.mocks.data import load_data_file, load_data_json
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import generate_kbase_token
import os
from unittest import mock

client = TestClient(app)

# config_yaml = load_data_file("config1.toml")


# @pytest.fixture
# def fake_fs(fs):
#     fs.create_file(utils.module_path("deploy/config.toml"), contents=config_yaml)
#     yield fs


TEST_LINK = load_data_json("link1.json")
TEST_LINK_BAR = load_data_json("link-bar.json")
MOCK_AUTH_PORT = 9999
MOCK_ORCID_OAUTH_PORT = 9997

@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_AUTH_PORT):
            yield


# @pytest.fixture(autouse=True)
# def around_tests(fake_fs):
#     config(True)
#     yield


def create_link(link_record):
    sm = storage_model.storage_model()
    sm.db.links.drop()
    sm.create_link_record(LinkRecord.model_validate(link_record))


#
# Tests
#


TEST_ENV = {
    "KBASE_ENDPOINT": f"http://foo/services/",
    "MODULE_DIR": os.environ.get("MODULE_DIR"),
    "MONGO_HOST": "mongo",
    "MONGO_PORT": "27017",
    "MONGO_DATABASE": "orcidlink",
    "MONGO_USERNAME": "dev",
    "MONGO_PASSWORD": "d3v",
    "ORCID_API_BASE_URL": "http://127.0.0.1:9998",
    "ORCID_OAUTH_BASE_URL": "http://127.0.0.1:9997",
}

@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_link(fake_fs):
    with mock_services():
        create_link(TEST_LINK)

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


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_get_link_shared(fake_fs):
    with mock_services():
        create_link(TEST_LINK_BAR)

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


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_is_linked(fake_fs):
    with mock_services():
        create_link(TEST_LINK)

        client = TestClient(app)
        response = client.get(
            "/link/is_linked", headers={"Authorization": generate_kbase_token("foo")}
        )
        result = response.json()
        assert result is True

        response = client.get(
            "/link/is_linked", headers={"Authorization": generate_kbase_token("bar")}
        )
        result = response.json()
        assert result is False

        response = client.get(
            "/link/is_linked", headers={"Authorization": generate_kbase_token("baz")}
        )
        assert response.status_code == 401

        response = client.get("/link/is_linked", headers={"Authorization": "baz"})
        assert response.status_code == 422


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_delete_link(fake_fs):
    with no_stderr():
        with mock_auth_service(MOCK_AUTH_PORT):
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                create_link(TEST_LINK)

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
