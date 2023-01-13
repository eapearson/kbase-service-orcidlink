import json
import uuid

import httpx
from orcidlink.service_clients.error import ServiceError


class GenericClient(object):
    def __init__(self, url=None, module=None, token=None, timeout=None):
        # Required parameters
        if url is None:
            raise TypeError('The "url" named argument is required')
        self.url = url

        if module is None:
            raise TypeError('The "module" named argument is required')
        self.module = module

        if timeout is None:
            raise TypeError('The "timeout" named argument is required')
        # Note that we operate with ms time normally, but httpx uses
        # seconds float.
        self.timeout = timeout

        # Optional parameters
        self.token = token

    def call_func(self, func_name, params=None, timeout=None):
        # Since this is designed to call KBase JSONRPC 1.1 services, we
        # follow the KBase conventions:
        # - params are always wrapped in an array; this emulates positional arguments
        # - a method with no arguments is called as either missing params in the call
        #   or the value None, and represented as an empty array in the service call
        # - a method with params is called with a single argument value which must be
        #   convertable to JSON; it is represented in the call to the service as an array
        #   wrapping that value.
        # Note that KBase methods can take multiple positional arguments (multiple elements
        # in the array), but by far most take just a single argument; this library makes that
        # simplifying assumption.
        if params is None:
            wrapped_params = []
        else:
            wrapped_params = [params]

        # The standard jsonrpc 1.1 calling object, with KBase conventions.
        # - id should be unique for this call (thus uuid), but is unused; it isn't
        #   really relevant for jsonrpc over http since each request always has a
        #   corresponding response; but it could aid in debugging since it connects
        #   the request and response.
        # - method is always the module name, a period, and the function name
        # - version is always 1.1 (even though there was no officially published jsonrpc 1.1)
        # - params as discussed above.
        call_params = {
            "id": str(uuid.uuid4()),
            "method": self.module + "." + func_name,
            "version": "1.1",
            "params": wrapped_params,
        }

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
            raise ServiceError(
                code=1401,
                name="JSONRPCError",
                message="Timeout calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except httpx.TransportError as rte:
            raise ServiceError(
                code=1402,
                name="JSONRPCError",
                message="Connection error calling service endpoint",
                data={
                    "url": self.url,
                    "headers": header,
                    "timeout": timeout,
                    "python_exception_string": str(rte),
                },
            )
        except Exception as ex:
            raise ServiceError(
                code=1500,
                name="JSONRPCError",
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
                    if response.status_code < 300:
                        raise ServiceError(
                            code=1100,
                            name="JSONRPCError",
                            message="Invalid response from upstream service - not json",
                            data={
                                "url": self.url,
                                "headers": header,
                                "decoding_error": str(err),
                                "response_text": response.content,
                                "status_code": response.status_code
                            },
                        )
                    else:
                        raise ServiceError(
                            code=1101,
                            name="JSONRPCError",
                            message="Invalid error response from upstream service - not json",
                            data={
                                "url": self.url,
                                "headers": header,
                                "decoding_error": str(err),
                                "response_text": response.content,
                            },
                        )
                else:
                    error = response_data.get("error")
                    if error is not None:
                        # Here we convert from the upstream KBase JSONRPC 1.1 error response
                        # to a JSONRPC 2.0 compatible exception. We pluck off commonly used
                        # error properties and put them into the data property. We do
                        # retain the error code (which should be JSONRPC 1.1 & 2.0 compatible).
                        error_data = {
                            "stack": error.get("error"),
                            "name": error.get("name"),
                        }
                        message = error.get("message")
                        if message is None:
                            message = error.get("name")
                        raise ServiceError(
                            code=error.get("code"),
                            name=error.get("name", "JSONRPCError"),
                            message=message,
                            data=error_data,
                        )

                    result = response_data.get("result")

                    # The normal response has a result property which, like the params, is
                    # wrapped in an array. In this case the array emulates multiple return values.
                    # By far most KBase services keep that to a single array element, and provide
                    # multiple values if need be (most do) by using an object as the array element.
                    # This is normally what developers refer to as the "results" (plural), and why
                    # we perform the following simplification.
                    #
                    # In the context of JSON-RPC, we view "results" as the array itself, with each
                    # element a single result item, but here we bend to convention.
                    #
                    if isinstance(result, list):
                        if len(result) > 0:
                            # Simplify the result to just the first element.
                            # If there is a need for supporting multiple result
                            # items, use either a custom client or GenericClient.
                            return result[0]
                        else:
                            # Simplify an empty result to None (null)
                            return None

                    # The one exception is when the result is just "null", which emulates a method
                    # with no, or void, result value.
                    elif result is None:
                        # None itself may be supplied as an empty result, rather than [].
                        return result
                    else:
                        # Any other result value is considered an error.
                        raise ServiceError(
                            code=1300,
                            name="JSONRPCError",
                            message=(
                                "Unexpected type in upstream service result; "
                                "must be array or null"
                            ),
                            data={
                                "url": self.url,
                                "headers": header,
                                "result": result,
                                "result_type": type(result).__name__,
                            },
                        )

                # Otherwise, if the service does not return json and has a 4xx or 5xx response,
                # raise an HTTPError from httpx. This will be caught by the caller and
                # converted to a general purpose "unknown error" jsonrpc error response.
                response.raise_for_status()

                # If we get here, the response status is < 400 and not of type application/json,
                # thus an invalid response.
                raise ServiceError(
                    code=104,
                    name="JSONRPCError",
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
            else:
                raise ServiceError(
                    code=1200,
                    name="JSONRPCError",
                    message="Invalid response from upstream service - expected 'application/json'",
                    data={
                        "url": self.url,
                        "headers": header,
                        "response_text": response.content,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type")
                    },
                )
