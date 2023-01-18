import pytest
from fastapi.testclient import TestClient
from orcidlink.main import app
from test.data.utils import load_data_file, load_data_json
from test.mocks.mock_contexts import mock_auth_service, no_stderr

client = TestClient(app, raise_server_exceptions=False)

config_yaml = load_data_file("config1.yaml")
kbase_yaml = load_data_file("kbase1.yml")


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml)
    fs.create_file("/kb/module/kbase.yml", contents=kbase_yaml)
    fs.add_real_directory("/kb/module/src/test/data")
    yield fs


TEST_LINK = load_data_json("link1.json")


# Happy paths


def test_docs(fake_fs):
    response = client.get("/docs")
    assert response.status_code == 200


def test_docs_error(fake_fs):
    openapi_url = app.openapi_url
    app.openapi_url = None
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/docs")
    assert response.status_code == 404
    # TODO: test assertions about this..
    app.openapi_url = openapi_url


# Error conditions


def test_main_404(fake_fs):
    response = client.get("/foo")
    assert response.status_code == 404


def test_validation_exception_handler(fake_fs):
    response = client.post("/works", json={"foo": "bar"})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"
    content = response.json()
    assert content["code"] == "requestParametersInvalid"
    assert content["title"] == "Request Parameters Invalid"
    assert (
        content["message"]
        == "This request does not comply with the schema for this endpoint"
    )


def test_kbase_auth_exception_handler(fake_fs):
    with no_stderr():
        with mock_auth_service() as [_, _, url]:
            # call with missing token
            response = client.get("/link", headers={})
            assert response.status_code == 401
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "missingToken"
            assert content["title"] == "Missing Token"
            assert content["message"] == "API call requires a KBase auth token"

            # call with invalid token
            response = client.get("/link", headers={"Authorization": "baz"})
            assert response.status_code == 401
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "invalidToken"
            assert content["title"] == "KBase auth token is invalid"

            # make a call which triggers a bug to trigger a JSON parse error
            response = client.get("/link", headers={"Authorization": "bad_json"})
            assert response.status_code == 500
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "authError"
            assert content["title"] == "Unknown error authenticating with KBase"

            # make a call which triggers a bug to trigger a JSON parse error
            response = client.get("/link", headers={"Authorization": "something_bad"})
            assert response.status_code == 500
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "internalServerError"
            assert content["title"] == "Internal Server Error"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case a method not supported.
            response = client.post(
                "/linx", headers={"Authorization": "internal_server_error"}
            )
            assert response.status_code == 404
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "notFound"
            assert content["title"] == "Not Found"
            assert content["message"] == "The requested resource was not found"
            assert content["data"]["detail"] == "Not Found"
            assert content["data"]["path"] == "/linx"

            # make some call which triggers a non-404 error caught by FastAPI/Starlette, in this
            # case a method not supported.
            response = client.post(
                "/link", headers={"Authorization": "internal_server_error"}
            )
            assert response.status_code == 405
            assert response.headers["content-type"] == "application/json"
            content = response.json()
            assert content["code"] == "fastapiError"
            assert content["title"] == "FastAPI Error"
            assert content["message"] == "Internal FastAPI Exception"
            assert content["data"]["detail"] == "Method Not Allowed"
