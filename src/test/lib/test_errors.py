import pytest

from orcidlink.lib import errors, exceptions

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
    assert exception.status_code == errors.ERRORS.internal_server_error.status_code
    assert exception.code == errors.ERRORS.internal_server_error.code
    assert exception.message == "Hello, I'm an internal error"
