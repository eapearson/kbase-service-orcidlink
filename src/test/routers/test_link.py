import contextlib

import pytest
from fastapi.testclient import TestClient
from orcidlink.lib.config import config
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.storage import storage_model
from test.data.utils import load_data_file, load_data_json
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import generate_kbase_token

client = TestClient(app)

config_yaml = load_data_file("config1.toml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.toml", contents=config_yaml)
    yield fs


TEST_LINK = load_data_json("link1.json")


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            yield


@pytest.fixture(autouse=True)
def around_tests(fake_fs):
    config(True)
    yield


def create_link():
    sm = storage_model.storage_model()
    sm.db.links.drop()
    sm.create_link_record(LinkRecord.parse_obj(TEST_LINK))


#
# Tests
#


def test_get_link(fake_fs):
    with mock_services():
        create_link()

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


def test_is_linked(fake_fs):
    with mock_services():
        create_link()

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


def test_delete_link(fake_fs):
    with no_stderr():
        with mock_auth_service():
            with mock_orcid_oauth_service():
                create_link()

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
