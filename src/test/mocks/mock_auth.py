import json

from orcidlink.lib import utils
from test.mocks.mock_server import MockService


def load_test_data(filename: str):
    test_data_path = (
        f"{utils.module_dir()}/src/test/service_clients/test_KBaseAuth/{filename}.json"
    )
    with open(test_data_path) as fin:
        return json.load(fin)


class MockAuthServiceBase(MockService):
    @staticmethod
    def error_no_token():
        return {
            "error": {
                "httpcode": 400,
                "httpstatus": "Bad Request",
                "appcode": 10010,
                "apperror": "No authentication token",
                "message": "10010 No authentication token: No user token provided",
                "callid": "abc",
                "time": 123,
            }
        }

    @staticmethod
    def error_invalid_token():
        return {
            "error": {
                "httpcode": 401,
                "httpstatus": "Unauthorized",
                "appcode": 10020,
                "apperror": "Invalid Token",
                "message": "10020 Invalid Token",
                "callid": "123",
                "time": 123,
            }
        }


GET_TOKEN_FOO = load_test_data("get-token-foo")
GET_TOKEN_BAR = load_test_data("get-token-bar")


class MockAuthService(MockAuthServiceBase):
    def do_GET(self):
        # TODO: Reminder - switch to normal auth2 endpoint in config and here.
        if self.path == "/services/auth/api/V2/token":
            authorization = self.headers.get("authorization")
            if authorization is None:
                self.send_json_error(self.error_no_token())
            else:
                if authorization == "foo":
                    # output_data = {
                    #     "user_id": "bar"
                    # }
                    self.send_json(GET_TOKEN_FOO)
                elif authorization == "bar":
                    # output_data = {
                    #     "user_id": "bar"
                    # }
                    self.send_json(GET_TOKEN_BAR)
                elif authorization == "exception":
                    self.send_json_error(self.error_no_token())
                elif authorization == "bad_json":
                    self.send_text("Bad JSON!")
                elif authorization == "something_bad":
                    # just do something bad:
                    x = 1 / 0
                    print(x)
                elif authorization == "internal_server_error":
                    self.send_text_error("Internal Server Error")
                else:
                    self.send_json_error(self.error_invalid_token())
