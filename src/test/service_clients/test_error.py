import pytest
from orcidlink.service_clients.error import ServiceError


def test_ServiceError():
    # Minimal
    error = ServiceError(code=123, name="foo", message="bar")
    assert error.code == 123
    assert error.name == "foo"
    assert error.message == "bar"

    # Maximal
    data = {"abc": 456}
    error = ServiceError(code=123, name="foo", message="bar", data=data)
    assert error.code == 123
    assert error.name == "foo"
    assert error.message == "bar"
    assert error.data == data


def test_ServiceError_errors():
    with pytest.raises(ValueError) as ex:
        ServiceError(name="foo", message="bar")
    assert str(ex.value) == 'The "code" named argument is required'

    with pytest.raises(ValueError) as ex:
        ServiceError(
            code=123,
            message="bar",
        )
    assert str(ex.value) == 'The "name" named argument is required'

    with pytest.raises(ValueError) as ex:
        ServiceError(code=123, name="foo")
    assert str(ex.value) == 'The "message" named argument is required'
