import contextlib

import pytest
from orcidlink.service_clients.GenericClient import GenericClient
from orcidlink.service_clients.error import ServiceError
from test.mocks.mock_contexts import mock_imaginary_service, no_stderr


class ImaginaryServiceClient(GenericClient):
    def __init__(self, url=None, token=None, timeout=None):
        super().__init__(url, "ImaginaryService", token, timeout)

    def status(self):
        return self.call_func(
            "status"
        )

    def adder(self, number1: int, number2: int):
        return self.call_func(
            "adder",
            {
                "number1": number1,
                "number2": number2
            }
        )

    def wait(self, wait_for: int):
        return self.call_func(
            "wait", {
                "for": wait_for
            }
        )

    def authorized(self):
        return self.call_func(
            "authorized"
        )

    def some_result(self, result):
        return self.call_func(
            "some_result", {
                "result": result
            }
        )

    # Errors

    def some_error(self, error):
        return self.call_func(
            "some_error", {
                "error": error
            }
        )

    # Various malformed responses

    def json_text_result(self):
        return self.call_func(
            "json_text_result"
        )

    def json_text_error(self):
        return self.call_func(
            "json_text_error"
        )

    def text_result(self):
        return self.call_func(
            "text_result"
        )

    def text_error(self):
        return self.call_func(
            "text_error"
        )


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_imaginary_service() as [_, _, url]:
            yield url


def test_constructor_errors():
    with pytest.raises(TypeError, match='The "url" named argument is required') as ex:
        ImaginaryServiceClient()

    with pytest.raises(TypeError, match='The "timeout" named argument is required') as ex:
        ImaginaryServiceClient(
            url=f"http:/foo/services/imaginary_service"
        )

    with pytest.raises(TypeError, match='The "url" named argument is required') as ex:
        ImaginaryServiceClient(
            timeout=1
        )


def test_status():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token=None
        )
        result = client.status()
        assert result is not None
        assert result.get("state") == "OK"


def test_adder_happy():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token=None
        )
        result = client.adder(40, 2)
        assert result is not None
        assert result.get("result") == 42


def test_empty_result():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token=None
        )
        result = client.some_result([])
        assert result is None

        result = client.some_result(None)
        assert result is None


def test_invalid_result():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token=None
        )

        with pytest.raises(ServiceError) as ex:
            client.some_result(123)

        assert ex.value.code == 1300


def test_authorized():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token="mytoken"
        )
        result = client.authorized()
        assert result is not None
        assert result.get("token") == "mytoken"


def test_timeout():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=0.1,
            token=None
        )
        with pytest.raises(ServiceError) as ex:
            client.wait(1)

        assert ex.value.code == 1401


def test_bad_url():
    with mock_services():
        client = ImaginaryServiceClient(
            url=f"http://127.0.0.2:1234/services/imaginary_service",
            timeout=0.1,
            token=None
        )
        with pytest.raises(ServiceError) as ex:
            client.wait(1)

        assert ex.value.code == 1402


def test_exception():
    with mock_services():
        client = ImaginaryServiceClient(
            url=f"http://127.0.0.2:1234/services/imaginary_service",
            timeout=-10,
            token=None
        )
        with pytest.raises(ServiceError) as ex:
            client.status()

        assert ex.value.code == 1500


def test_json_text():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=1,
            token=None
        )

        with pytest.raises(ServiceError) as ex:
            client.json_text_result()

        assert ex.value.code == 1100

        with pytest.raises(ServiceError) as ex:
            client.json_text_error()

        assert ex.value.code == 1101

        with pytest.raises(ServiceError) as ex:
            client.text_result()

        assert ex.value.code == 1200

        with pytest.raises(ServiceError) as ex:
            client.text_error()

        assert ex.value.code == 1200


def test_some_error():
    with mock_services() as url:
        client = ImaginaryServiceClient(
            url=url,
            timeout=10,
            token=None
        )
        with pytest.raises(ServiceError) as ex:
            client.some_error({
                "code": 123,
                "name": "some error name",
                "message": "some error message",
                "error": "some error error"
            })

        assert ex.value.code == 123
        assert ex.value.name == "some error name"
        assert ex.value.message == "some error message"

        with pytest.raises(ServiceError) as ex:
            client.some_error({
                "code": 1234,
                "name": "some error name"
            })

        assert ex.value.code == 1234
        assert ex.value.name == "some error name"
        assert ex.value.message == "some error name"
