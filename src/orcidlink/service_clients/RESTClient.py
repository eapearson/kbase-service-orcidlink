import json

import httpx
from orcidlink.service_clients.error import ServiceError


class RESTError(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class RESTClient(object):
    def __init__(self, url=None, timeout=None, token=None):
        if url is None:
            raise ValueError('The "url" argument is required')

        if timeout is None:
            raise ValueError('The "timeout" argument is required')

        self.token = token
        self.url = url
        # Note that we operate with ms time normally, but httpx uses
        # seconds float.
        self.timeout = timeout

    def post(self, path, payload=None, extra_header=None, params=None, timeout=None):
        header = {"Content-Type": "application/json", "Accept": "application/json"}

        if extra_header is not None:
            for key, value in extra_header.items():
                header[key] = value

        # Calls may be authorized or not with a KBase token.
        if self.token:
            header["Authorization"] = self.token

        timeout = timeout or self.timeout

        url = f"{self.url}/{path}"

        if payload is None:
            data = None
        else:
            data = json.dumps(payload)

        try:
            response = httpx.post(
                url,
                headers=header,
                content=data,
                params=params,
                timeout=timeout,
            )
        except httpx.ReadTimeout as rte:
            raise ServiceError(
                code=100,
                message="Timeout calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except httpx.TransportError as rte:
            # Note that ServiceError mirrors (and is eventually converted to)
            # a JSONRPC 2.0 error.
            raise ServiceError(
                code=100,
                message="Timeout calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except Exception as ex:
            raise ServiceError(
                code=101,
                message="Error calling service endpoint: " + ex.message,
                data={
                    "url": self.url,
                    "headers": header,
                },
            )
        else:
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    response_data = response.json()
                except json.decoder.JSONDecodeError as err:
                    raise ServiceError(
                        code=102,
                        message="Invalid response from upstream service - not json",
                        data={
                            "url": self.url,
                            "headers": header,
                            "decoding_error": str(err),
                            "response_text": response.content,
                        },
                    )
                else:
                    if response.status_code >= 300:
                        raise RESTError(
                            response.status_code,
                            f"Unexpected {response.status_code} response",
                            data=response_data,
                        )
                    else:
                        return response_data
            elif response.headers.get("content-type", "").startswith("text/plain"):
                if response.status_code >= 300:
                    raise RESTError(
                        response.status_code,
                        "Unexpected 3xx response",
                        data={"text": response.text},
                    )
                else:
                    return response.text

            else:
                raise ServiceError(
                    code=104,
                    message=(
                        "Invalid response from upstream service; "
                        "not application/json or text/plain"
                    ),
                    data={
                        "url": self.url,
                        "headers": header,
                        "response_status": response.status_code,
                        "response_content_type": response.headers.get(
                            "content-type", None
                        ),
                        "response_content": response.content,
                    },
                )

    def get(self, path, params=None, timeout=None):
        header = {"Content-Type": "application/json", "Accept": "application/json"}

        # Calls may be authorized or not with a KBase token.
        if self.token:
            header["Authorization"] = self.token

        timeout = timeout or self.timeout

        url = f"{self.url}/{path}"

        try:
            response = httpx.get(url, headers=header, params=params, timeout=timeout)
        except httpx.ReadTimeout as rte:
            raise ServiceError(
                code=100,
                message="Timeout calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except httpx.TransportError as rte:
            # Note that ServiceError mirrors (and is eventually converted to)
            # a JSONRPC 2.0 error.
            raise ServiceError(
                code=100,
                message="Timeout calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except Exception as ex:
            raise ServiceError(
                code=101,
                message="Error calling service endpoint: " + str(ex),
                data={
                    "url": self.url,
                    "headers": header,
                },
            )
        else:
            if response.headers.get("content-type", "").startswith("application/json"):
                try:
                    response_data = response.json()
                except json.decoder.JSONDecodeError as err:
                    raise ServiceError(
                        code=102,
                        message="Invalid response from upstream service - not json",
                        data={
                            "url": self.url,
                            "headers": header,
                            "decoding_error": str(err),
                            "response_text": response.content,
                        },
                    )
                else:
                    if response.status_code >= 300:
                        raise RESTError(
                            response.status_code,
                            f"Unexpected {response.status_code} response",
                            data=response_data,
                        )
                    else:
                        return response_data
            elif response.headers.get("content-type", "").startswith("text/plain"):
                if response.status_code >= 300:
                    raise RESTError(
                        response.status_code,
                        "Unexpected 3xx response",
                        data={"text": response.text},
                    )
                else:
                    return response.text

            else:
                raise ServiceError(
                    code=104,
                    message=(
                        "Invalid response from upstream service; "
                        "not application/json or text/plain"
                    ),
                    data={
                        "url": self.url,
                        "headers": header,
                        "response_status": response.status_code,
                        "response_content_type": response.headers.get(
                            "content-type", None
                        ),
                        "response_content": response.content,
                    },
                )
