import json

import pytest
from pydantic import Field

from orcidlink.lib import errors, exceptions
from orcidlink.lib.type import ServiceBaseModel

# def test_ServiceError():
#     # Minimal
#     error = ServiceError(code=123, name="foo", message="bar")
#     assert error.code == 123
#     assert error.name == "foo"
#     assert error.message == "bar"
#
#     # Maximal
#     data = {"abc": 456}
#     error = ServiceError(code=123, name="foo", message="bar", data=data)
#     assert error.code == 123
#     assert error.name == "foo"
#     assert error.message == "bar"
#     assert error.data == data
#
#
# def test_ServiceError_errors():
#     with pytest.raises(ValueError) as ex:
#         ServiceError(name="foo", message="bar")
#     assert str(ex.value) == 'The "code" named argument is required'
#
#     with pytest.raises(ValueError) as ex:
#         ServiceError(
#             code=123,
#             message="bar",
#         )
#     assert str(ex.value) == 'The "name" named argument is required'
#
#     with pytest.raises(ValueError) as ex:
#         ServiceError(code=123, name="foo")
#     assert str(ex.value) == 'The "message" named argument is required'

# def test_make_service_error():
#     with pytest.raises(ServiceError, match="message") as ex:
#         raise make_service_error(
#             "codex", "title", "message", data={"foo": "bar"}, status_code=123
#         )
#
#     response = ex.value.get_response()
#     assert response is not None
#     assert response.status_code == 123


def test_internal_server_error():
    with pytest.raises(exceptions.InternalServerError) as ie:
        raise exceptions.InternalServerError("Hello, I'm an internal error")
    exception = ie.value
    # assert exception.status_code == errors.ERRORS.internal_server_error.status_code
    assert exception.error.code == errors.ERRORS.internal_server_error.code
    assert exception.message == "Hello, I'm an internal error"


def test_service_error_no_data():
    with pytest.raises(exceptions.ServiceErrorY) as ie:
        raise exceptions.ServiceErrorY(
            errors.ERRORS.impossible_error, "Hello, I'm an impossible error"
        )
    exception = ie.value
    assert exception.message == "Hello, I'm an impossible error"
    assert exception.data is None

    response = exception.get_response()

    # We can't inspect the response object much, but we can convert to JSON and make sure
    # we are happy with it.
    response_json = json.loads(response.body)
    assert "code" in response_json
    assert "title" in response_json
    assert "message" in response_json
    assert "data" not in response_json


def test_service_error_with_data():
    class TestData(ServiceBaseModel):
        foo: str = Field(...)

    with pytest.raises(exceptions.ServiceErrorY) as ie:
        raise exceptions.ServiceErrorY(
            errors.ERRORS.impossible_error,
            "Hello, I'm an impossible error",
            data=TestData(foo="bar'"),
        )
    exception = ie.value
    assert exception.message == "Hello, I'm an impossible error"
    assert exception.data is not None

    response = exception.get_response()

    # We can't inspect the response object much, but we can convert to JSON and make sure
    # we are happy with it.
    response_json = json.loads(response.body)
    assert "code" in response_json
    assert "title" in response_json
    assert "message" in response_json
    assert "data" in response_json
    data = response_json["data"]
    assert "foo" in data
