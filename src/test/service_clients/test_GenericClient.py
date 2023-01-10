import contextlib

import pytest
from orcidlink.service_clients.GenericClient import GenericClient
from orcidlink.service_clients.error import INVALID_PARAMS, METHOD_NOT_FOUND, ServiceError
from test.mocks.mock_contexts import mock_jsonrpc11_service, no_stderr


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_jsonrpc11_service() as [_, _, url]:
            yield url


def test_constructor():
    client = GenericClient(
        module="foo",
        url="bar",
        timeout=1
    )
    assert client is not None


def test_constructor_errors():
    with pytest.raises(TypeError) as ex:
        GenericClient()
        assert ex is not None

    with pytest.raises(TypeError) as ex:
        GenericClient(
            module="foo"
        )

    with pytest.raises(TypeError) as ex:
        GenericClient(
            module="foo",
            url="bar"
        )

    with pytest.raises(TypeError) as ex:
        GenericClient(
            module="foo",
            timeout=1
        )

    with pytest.raises(TypeError) as ex:
        GenericClient(
            url="bar"
        )

    with pytest.raises(TypeError) as ex:
        GenericClient(
            url="bar",
            timeout=1
        )

    with pytest.raises(TypeError) as ex:
        GenericClient(
            timeout=1
        )


def test_call_func():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        result = client.call_func("foo", params={
            "foo": "bar"
        })
        assert result is not None
        assert isinstance(result, dict)
        assert 'result'
        assert result['bar'] == 'baz'


def test_call_func_no_params():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        result = client.call_func("no_params")
        assert result is not None
        assert isinstance(result, dict)
        assert 'result'
        assert result['bar'] == 'baz'


def test_call_func_no_params_has_params():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        # with pytest.raises(ServiceError, match="Invalid params") as ex:
        #     client.call_func("no_params", {"foo": "bar"})
        # assert ex.value.code == INVALID_PARAMS
        # assert ex.value.message == "Invalid params"

        # NB: pytest.raises interferes with the server stopping
        with pytest.raises(ServiceError) as ex:
            client.call_func("no_params", {"foo": "bar"})

        assert ex.value.code == INVALID_PARAMS
        assert ex.value.message == "Invalid params"


def test_call_func_method_not_found():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("fooey", params={
                "foo": "bar"
            })

        assert ex.value.code == METHOD_NOT_FOUND
        assert ex.value.message == "Method not found"


def test_call_func_with_authorization():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token="mytoken"
        )
        # Honestly, there is no way to tell if a service which
        # accepts authorization got it ... other than its behavior
        # if it utilizes it. And ... we don't have a standard
        # way of handling the case in which auth is required but
        # absent or invalid.
        # Here we just have a test client which reflects the token back.
        result = client.call_func("with_authorization")
        assert result.get("token") == "mytoken"


def test_call_func_with_authorization_invalid():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token="mytokenx"
        )
        # Honestly, there is no way to tell if a service which
        # accepts authorization got it ... other than its behavior
        # if it utilizes it. And ... we don't have a standard
        # way of handling the case in which auth is required but
        # absent or invalid.
        # Here we just have a test client which reflects the token back.

        with pytest.raises(ServiceError) as ex:
            client.call_func("with_authorization")

        assert ex.value.code == -32400


def test_call_func_with_authorization_missing():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        # Honestly, there is no way to tell if a service which
        # accepts authorization got it ... other than its behavior
        # if it utilizes it. And ... we don't have a standard
        # way of handling the case in which auth is required but
        # absent or invalid.
        # Here we just have a test client which reflects the token back.
        with pytest.raises(ServiceError) as ex:
            client.call_func("with_authorization")
        assert ex.value.code == -32500


def test_call_func_returns_text():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("result_text")

        assert ex.value.code == 1200


def test_call_func_returns_json_text():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("result_json_text")

        assert ex.value.code == 1100


def test_call_func_error_returns_text():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("error_text")

        assert ex.value.code == 1200


def test_call_func_error_returns_json_text():
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("error_json_text")

        assert ex.value.code == 1101


def test_call_func_empty_result():
    """
     When a service method has no results to return, an empty list is used.
     This is nice, because it allows the result to be truly void.
     The caller should just ignore the result, but it is returned as null (None)
     in the client (to be consistent with the next case -- actually
     returning null!)
    """

    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        result = client.call_func("empty_result")
        assert result is None


def test_call_func_null_result():
    """
     Similar to the above case, but some service methods, and the SDK-based apps in general,
     will return `null` rather than `[]`.
    """

    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
            token=None
        )
        result = client.call_func("null_result")
        assert result is None


def test_call_func_invalid_result():
    """
     Similar to the above case, but some service methods, and the SDK-based apps in general,
     will return `null` rather than `[]`.
    """

    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("invalid_result")

        assert ex.value.code == 1300


def test_call_func_connection_error():
    """
     Similar to the above case, but some service methods, and the SDK-based apps in general,
     will return `null` rather than `[]`.
    """
    client = GenericClient(
        module="MyServiceModule",
        url=f"http://127.0.0.2:8888/services/my_service",
        timeout=1,
    )

    with pytest.raises(ServiceError) as ex:
        client.call_func("no_params")

    assert ex.value.code == 1402


def test_call_func_timeout_error():
    """
     Similar to the above case, but some service methods, and the SDK-based apps in general,
     will return `null` rather than `[]`.
    """
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=0.1,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("wait", {"for": 1})
        assert ex.value.code == 1401


def test_call_func_exception_error():
    """
    This should primarily be caused by GenericClient usage errors, but could
    also be due to internal programming errors.
    """
    with mock_services() as url:
        client = GenericClient(
            module="MyServiceModule",
            url=url,
            timeout=-10,
        )
        with pytest.raises(ServiceError) as ex:
            client.call_func("wait", {"for": 1})

        assert ex.value.code == 1500
