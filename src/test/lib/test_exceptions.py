import json

import pytest
from pydantic import Field

from orcidlink.lib import errors, exceptions
from orcidlink.lib.service_clients.jsonrpc import JSONRPCError
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

    # We can't inspect the response object much, but we can convert to JSON and make
    # sure we are happy with it.
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

    # We can't inspect the response object much, but we can convert to JSON and make
    # sure we are happy with it.
    response_json = json.loads(response.body)
    assert "code" in response_json
    assert "title" in response_json
    assert "message" in response_json
    assert "data" in response_json
    data = response_json["data"]
    assert "foo" in data


def test_upstream_jsonrpc_error_error():
    error = JSONRPCError(
        code=123, message="This is a JSONRPC Error", data={"foo": "bar"}
    )
    with pytest.raises(exceptions.UpstreamJSONRPCError) as ie:
        raise exceptions.UpstreamJSONRPCError(
            "Hello, I'm an upstream error", data=error
        )
    exception = ie.value
    # assert exception.status_code == errors.ERRORS.internal_server_error.status_code
    assert exception.error.code == errors.ERRORS.upstream_jsonrpc_error.code
    assert exception.message == "Hello, I'm an upstream error"


def test_upstream_error():
    with pytest.raises(exceptions.UpstreamError) as ie:
        raise exceptions.UpstreamError("Hello, I'm an upstream error")
    exception = ie.value
    # assert exception.status_code == errors.ERRORS.internal_server_error.status_code
    assert exception.error.code == errors.ERRORS.upstream_error.code
    assert exception.message == "Hello, I'm an upstream error"


def test_upstream_orcid_api_error():
    error = exceptions.UpstreamErrorData(
        status_code=123, message="my message", source="testing"
    )
    with pytest.raises(exceptions.UpstreamORCIDAPIError) as ie:
        raise exceptions.UpstreamORCIDAPIError(
            "Hello, I'm an orcid api error", data=error
        )
    exception = ie.value
    assert exception.error.code == errors.ERRORS.upstream_orcid_error.code
    assert exception.message == "Hello, I'm an orcid api error"


def test_impossible_error():
    with pytest.raises(exceptions.ImpossibleError) as ie:
        raise exceptions.ImpossibleError("Hello, I'm an impossible error")
    exception = ie.value
    assert exception.error.code == errors.ERRORS.impossible_error.code
    assert exception.message == "Hello, I'm an impossible error"


def test_alreadly_linked_error():
    with pytest.raises(exceptions.AlreadyLinkedError) as ie:
        raise exceptions.AlreadyLinkedError("Hello, I'm an already linked error")
    exception = ie.value
    assert exception.error.code == errors.ERRORS.already_linked.code
    assert exception.message == "Hello, I'm an already linked error"


def test_authorization_required_error():
    with pytest.raises(exceptions.AuthorizationRequiredError) as ie:
        raise exceptions.AuthorizationRequiredError(
            "Hello, I'm an authorization required error"
        )
    exception = ie.value
    assert exception.error.code == errors.ERRORS.authorization_required.code
    assert exception.message == "Hello, I'm an authorization required error"


def test_unauthorized_error():
    with pytest.raises(exceptions.UnauthorizedError) as ie:
        raise exceptions.UnauthorizedError("Hello, I'm an UnauthorizedError error")
    exception = ie.value
    assert exception.error.code == errors.ERRORS.not_authorized.code
    assert exception.message == "Hello, I'm an UnauthorizedError error"


def test_not_found_error():
    with pytest.raises(exceptions.NotFoundError) as ie:
        raise exceptions.NotFoundError("Hello, I'm an NotFoundError error")
    exception = ie.value
    assert exception.error.code == errors.ERRORS.not_found.code
    assert exception.message == "Hello, I'm an NotFoundError error"


def test_json_decode_error():
    data = exceptions.JSONDecodeErrorData(message="Foo and bar")
    with pytest.raises(exceptions.JSONDecodeError) as ie:
        raise exceptions.JSONDecodeError(
            "Hello, I'm an JSONDecodeError error", data=data
        )
    exception = ie.value
    assert exception.error.code == errors.ERRORS.json_decode_error.code
    assert exception.message == "Hello, I'm an JSONDecodeError error"


def test_content_type_error():
    with pytest.raises(exceptions.ContentTypeError) as ie:
        data = exceptions.ContentTypeErrorData(
            originalContentType="some bad content type"
        )
        raise exceptions.ContentTypeError(
            "Hello, I'm an ContentTypeError error", data=data
        )
    exception = ie.value
    assert exception.error.code == errors.ERRORS.content_type_error.code
    assert exception.message == "Hello, I'm an ContentTypeError error"


def test_orcid_profile_name_private_error():
    with pytest.raises(exceptions.ORCIDProfileNamePrivate) as ie:
        raise exceptions.ORCIDProfileNamePrivate("Name is private")
    exception = ie.value
    assert exception.error.code == errors.ERRORS.orcid_profile_name_private.code
    assert exception.message == "Name is private"
