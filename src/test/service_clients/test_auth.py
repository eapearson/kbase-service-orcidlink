import json

import pytest
from orcidlink.lib import utils
from orcidlink.service_clients import auth
from test.mocks.mock_contexts import mock_auth_service, no_stderr
from test.mocks.mock_server import MockService


def load_test_data(filename: str):
    test_data_path = f"{utils.module_dir()}/src/test/service_clients/test_auth/{filename}.json"
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
                "time": 123
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
                "time": 123
            }
        }


@pytest.fixture
def my_config_file(fs):
    fake_config = """
kbase:
  services:
    Auth2:
      url: http://127.0.0.1:9999/services/auth/api/V2/token
      tokenCacheLifetime: 300000
      tokenCacheMaxSize: 20000
    ServiceWizard:
      url: http://127.0.0.1:9999/services/service_wizard
  uiOrigin: https://ci.kbase.us
  defaults:
    serviceRequestTimeout: 60000
orcid:
  oauthBaseURL: https://sandbox.orcid.org/oauth
  baseURL: https://sandbox.orcid.org
  apiBaseURL: https://api.sandbox.orcid.org/v3.0
env:
  CLIENT_ID: 'REDACTED-CLIENT-ID'
  CLIENT_SECRET: 'REDACTED-CLIENT-SECRET'
  IS_DYNAMIC_SERVICE: 'yes'
    """
    fs.create_file("/kb/module/config/config.yaml", contents=fake_config)
    yield fs


GET_TOKEN_FOO = load_test_data("get-token-foo")


# class MockAuthService(MockAuthServiceBase):
#     def do_GET(self):
#         # TODO: Reminder - switch to normal auth2 endpoint in config and here.
#         if self.path == "/services/auth/api/V2/token":
#             authorization = self.headers.get('authorization')
#             if authorization is None:
#                 self.send_json_error(self.error_no_token())
#             else:
#                 if authorization == "foo":
#                     # output_data = load_test_data("get-token-foo")
#                     self.send_json(GET_TOKEN_FOO)
#                 elif authorization == "exception":
#                     self.send_json_error(self.error_no_token())
#                 elif authorization == "internal_server_error":
#                     self.send_text_error('Internal Server Error')
#                 else:
#                     self.send_json_error(self.error_invalid_token())


def test_auth_get_username(my_config_file):
    with no_stderr():
        with mock_auth_service():
            assert auth.get_username("foo") == "foo"
