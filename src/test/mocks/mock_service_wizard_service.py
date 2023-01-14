import json

from orcidlink.service_clients.error import (
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    SERVER_ERROR_MIN,
)
from test.mocks.mock_server import MockSDKJSON11ServiceBase


class MockServiceWizardService(MockSDKJSON11ServiceBase):
    def get_positional_params(self, request):
        method = request.get("method")
        positional_params = request.get("params")
        if positional_params is None:
            self.increment_method_call_count(method, "error")
            # Wrong, but we reflect it.
            return None, self.error_response(PARSE_ERROR, "Parse error")
        else:
            return positional_params[0], None

    def get_empty_positional_params(self, request):
        method = request.get("method")
        positional_params = request.get("params")
        if positional_params is None:
            self.increment_method_call_count(method, "error")
            # Wrong, but we reflect it.
            return None, self.error_response(PARSE_ERROR, "Parse error")
        elif len(positional_params) > 0:
            self.increment_method_call_count(method, "error")
            # Wrong, but we reflect it.
            return None, self.error_response(SERVER_ERROR_MIN, "Server error")
        else:
            return None, None

    # NB: Override this for different behavior.
    def send_service_status(self, method: str, module_name: str, version: str | None):
        if module_name == "ORCIDLink":
            if version == "dev" or version is None:
                self.increment_method_call_count(method, "success")
                self.send_json(
                    self.success_response(
                        {
                            "git_commit_hash": "HASH",
                            "status": "active",
                            "hash": "HASH",
                            "release_tags": ["dev"],
                            "url": "https://ci.kbase.us:443/dynserv/HASH.ORCIDLink",
                            "module_name": "ORCIDLink",
                            "health": "healthy",
                            "up": 1,
                        }
                    )
                )
            else:
                self.increment_method_call_count(method, "error")
                self.send_json(
                    self.error_response(
                        SERVER_ERROR_MIN,
                        "Server error",
                        message="'No module version found that matches your criteria!'",
                    )
                )
        else:
            self.increment_method_call_count(method, "error")
            self.send_json(
                self.error_response(
                    SERVER_ERROR_MIN,
                    "Server error",
                    message="'Module cannot be found based on module_name or git_url parameters.'",
                )
            )

    def do_POST(self):
        if self.path == "/services/service_wizard/rpc":
            request = json.loads(self.get_body_string())

            method = request.get("method")

            if method == "ServiceWizard.get_service_status":
                params, error = self.get_positional_params(request)
                if error is not None:
                    self.send_json(error)
                    return

                module_name = params.get("module_name")
                if module_name is None:
                    # Note this is wrong, because the ServiceWizard gets it wrong.
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            SERVER_ERROR_MIN, "Server error", message="'module_name'"
                        )
                    )
                    return

                # Version may be `null`, but Python has dicts great get() with an
                # undefined key and the value None as the same. JS ftw.
                if "version" not in params:
                    # TODO: this is correct, but ServiceWizard gets this wrong,
                    self.increment_method_call_count(method, "error")
                    self.send_json(
                        self.error_response(
                            SERVER_ERROR_MIN, "Server error", message="'version'"
                        )
                    )
                    return
                version = params.get("version")

                self.send_service_status(method, module_name, version)

            elif method == "ServiceWizard.status":
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
                            "git_url": "https://github.com/kbase/service_wizard",
                        }
                    )
                )
            else:
                self.increment_method_call_count(method, "error")
                self.send_json(
                    self.error_response(METHOD_NOT_FOUND, "Method not found")
                )
