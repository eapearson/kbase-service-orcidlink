import json
import time

from orcidlink.lib.errors import INVALID_PARAMS, METHOD_NOT_FOUND
from test.mocks.mock_server import MockSDKJSON11ServiceBase


class MockImaginaryService(MockSDKJSON11ServiceBase):
    def do_POST(self):
        if self.path == "/services/imaginary_service":
            request = json.loads(self.get_body_string())

            method = request.get("method")

            if method == "ImaginaryService.foo":
                params, error = self.get_positional_params(request)
                if error is not None:
                    self.send_json(error)
                    return
            elif method == "ImaginaryService.status":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.send_json(error)
                    return
                self.send_json(
                    self.success_response(
                        {
                            "git_commit_hash": "HASH",
                            "state": "OK",
                            "version": "0.4.2",
                            "message": "",
                            "git_url": "https://github.com/kbase/imaginary_service",
                        }
                    )
                )
            elif method == "ImaginaryService.adder":
                params, error = self.get_positional_params(request)
                number1 = params.get("number1")
                if number1 is None:
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'number1' is required",
                        )
                    )
                    return

                if not isinstance(number1, (int, float)):
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'number1' is not a number",
                        )
                    )
                    return

                number2 = params.get("number2")
                if number2 is None:
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'number2' is required",
                        )
                    )
                    return

                if not isinstance(number2, (int, float)):
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'number2' is not a number",
                        )
                    )
                    return

                return self.send_json(
                    self.success_response({"result": number1 + number2})
                )
            elif method == "ImaginaryService.wait":
                params, error = self.get_positional_params(request)
                wait_for = params.get("for")
                # fuggetabout param checking
                time.sleep(wait_for)
                return self.send_json(self.success_response({"waited": wait_for}))
            elif method == "ImaginaryService.authorized":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.increment_method_call_count(method, "error")
                    return self.send_json(self.error_response(error))

                self.increment_method_call_count(method, "success")
                return self.send_json(
                    self.success_response({"token": self.headers.get("authorization")})
                )
            elif method == "ImaginaryService.json_text_result":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.increment_method_call_count(method, "error")
                    return self.send_json(self.error_response(error))

                self.increment_method_call_count(method, "success")
                return self.send_json_text("This should fail")

            elif method == "ImaginaryService.json_text_error":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.increment_method_call_count(method, "error")
                    return self.send_json(self.error_response(error))

                self.increment_method_call_count(method, "success")
                return self.send_json_text_error("This should fail")

            elif method == "ImaginaryService.text_result":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.increment_method_call_count(method, "error")
                    return self.send_json(self.error_response(error))

                self.increment_method_call_count(method, "success")
                return self.send_text("This should fail")

            elif method == "ImaginaryService.text_error":
                params, error = self.get_empty_positional_params(request)
                if error is not None:
                    self.increment_method_call_count(method, "error")
                    return self.send_json(self.error_response(error))

                self.increment_method_call_count(method, "success")
                return self.send_text_error("This should fail")

            elif method == "ImaginaryService.some_error":
                params, error = self.get_positional_params(request)
                some_error = params.get("error")
                if some_error is None:
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'error' is required",
                        )
                    )
                    return

                self.increment_method_call_count(method, "error")
                return self.send_json_error(
                    self.error_data_response(some_error, call_id="12345")
                )
            elif method == "ImaginaryService.some_result":
                params, error = self.get_positional_params(request)
                if "result" not in params:
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            INVALID_PARAMS,
                            "Invalid params",
                            message="The parameter 'result' is required",
                        )
                    )
                    return

                some_result = params.get("result")

                self.increment_method_call_count(method, "success")
                return self.send_json(self.some_result(some_result, call_id="12345"))

            else:
                self.increment_method_call_count(method, "error")
                self.send_json(
                    self.error_response(METHOD_NOT_FOUND, "Method not found")
                )
