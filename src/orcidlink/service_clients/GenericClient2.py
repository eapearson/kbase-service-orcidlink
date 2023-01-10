import json
import uuid

import httpx
from orcidlink.service_clients.error import ServiceError


class GenericClient2(object):
    def __init__(self, module=None, url=None, token=None, timeout=None):
        # if module is None:
        #     raise ValueError('The "module" argument is required')
        if url is None:
            raise TypeError('The "url" argument is required')
        if timeout is None:
            raise TypeError('The "timeout" argument is required')

        self.module = module
        self.token = token
        self.url = url
        # Note that we operate with ms time normally, but httpx uses
        # seconds float.
        self.timeout = timeout

    def call_func(self, func_name, params=None, timeout=None):
        # The standard jsonrpc 1.1 calling object, with KBase conventions.
        # - id should be unique for this call (thus uuid), but is unused; it isn't
        #   really relevant for jsonrpc over http since each request always has a
        #   corresponding response; but it could aid in debugging since it connects
        #   the request and response.
        # - method is always the module name, a period, and the function name
        # - version is always 1.1 (even though there was no officially published jsonrpc 1.1)
        # - params as discussed above.
        if self.module is not None:
            method = f"{self.module}.{func_name}"
        else:
            method = func_name
        call_params = {"id": str(uuid.uuid4()), "method": method, "jsonrpc": "2.0"}

        if params is not None:
            call_params["params"] = params

        header = {"Content-Type": "application/json"}

        # Calls may be authorized or not with a KBase token.
        if self.token:
            header["Authorization"] = self.token

        timeout = timeout or self.timeout

        # Note that timeout should be set here (except for type errors).
        # The constructor requires it, and it can be overridden in the call
        # to this method.

        try:
            response = httpx.post(
                self.url, headers=header, content=json.dumps(call_params), timeout=timeout
            )

        except httpx.ReadTimeout as rte:
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
                    if "error" in response_data:
                        error = response_data["error"]
                        # Here we convert from the upstream KBase JSONRPC 1.1 error response
                        # to a JSONRPC 2.0 compatible exception. We pluck off commonly used
                        # error properties and put them into the data property. We do
                        # retain the error code (which should be JSONRPC 1.1 & 2.0 compatible).
                        error_data = {
                            "stack": error.get("error"),
                            "name": error.get("name"),
                        }
                        raise ServiceError(
                            code=error.get("code"),
                            message=error.get("message", error.get("name")),
                            data=error_data,
                        )

                    return response_data.get("result")
            else:
                # Otherwise, if the service does not return json and has a 4xx or 5xx response,
                # raise an HTTPError from http. This will be caught by the caller and
                # converted to a general purpose "unknown error" jsonrpc error response.
                response.raise_for_status()

                # If we get here, the response status is < 400 and not of type application/json,
                # thus an invalid response.
                raise ServiceError(
                    code=104,
                    message=(
                        "Invalid response from upstream service; "
                        "not application/json, not an error status"
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
