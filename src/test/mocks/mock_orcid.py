import json
import os
from test.mocks.data import load_test_data
from test.mocks.mock_server import MockService
from time import sleep
from urllib.parse import parse_qs

from orcidlink.lib import utils

TEST_DATA_DIR = os.environ["TEST_DATA_DIR"]


class MockORCIDAPI(MockService):
    def do_GET(self):
        if self.path == "/0000-0003-4997-3076/record":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "profile")
            self.send_json(test_data, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/email":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "email")
            self.send_json(test_data, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "works_x")
            self.send_json(test_data, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works/1526002":
            work_record = load_test_data(TEST_DATA_DIR, "orcid", "work_1526002")
            self.send_json(work_record, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works/1487805":
            work_record = load_test_data(TEST_DATA_DIR, "orcid", "work_1487805")
            self.send_json(work_record, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works/123":
            print("GETting", self.path)
            self.send_text("foobar")

        elif self.path == "/0000-0003-4997-3076/works/456":
            error = {
                "response-code": 400,
                "developer-message": (
                    "The client application sent a bad request to ORCID. "
                    'Full validation error: For input string: "1526002x"'
                ),
                "user-message": "The client application sent a bad request to ORCID.",
                "error-code": 9006,
                "more-info": "https://members.orcid.org/api/resources/troubleshooting",
            }
            self.send_json_error(error, 400, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works/notsource":
            error = {
                "response-code": 403,
                "developer-message": (
                    "403 Forbidden: You are not the source of the work, "
                    "so you are not allowed to update it."
                ),
                "user-message": (
                    "The client application is not the source of the resource "
                    "it is trying to access."
                ),
                "error-code": 9010,
                "more-info": "https://members.orcid.org/api/resources/troubleshooting",
            }
            self.send_json_error(error, 403, "application/vnd.orcid+json")
        else:
            raise Exception("Not a supported mock case")

    def do_DELETE(self):
        if self.path == "/0000-0003-4997-3076/work/1526002":
            # work_record = load_test_data(TEST_DATA_DIR, "orcid", "work_1526002")
            # test_data = {"bulk": [{"work": work_record}]}
            self.send_empty()
        elif self.path == "/0000-0003-4997-3076/work/123":
            error = {
                "response-code": 403,
                "developer-message": (
                    "403 Forbidden: You are not the source of the work, "
                    "so you are not allowed to update it."
                ),
                "user-message": (
                    "The client application is not the source of the resource "
                    "it is trying to access."
                ),
                "error-code": 9010,
                "more-info": "https://members.orcid.org/api/resources/troubleshooting",
            }
            self.send_json_error(error, 403, "application/vnd.orcid+json")
        elif self.path == "/0000-0003-4997-3076/work/456":
            error = {
                "response-code": 404,
                "developer-message": (
                    "404 Not Found: The resource was not found. Full validation error: "
                    "No entity found for query"
                ),
                "user-message": "The resource was not found.",
                "error-code": 9016,
                "more-info": "https://members.orcid.org/api/resources/troubleshooting",
            }
            self.send_json_error(error, 404, "application/vnd.orcid+json")

    def do_PUT(self):
        if self.path == "/0000-0003-4997-3076/work/1526002":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "work_1526002")["bulk"][
                0
            ]["work"]

            # simulates an updated last modified date.
            test_data["last-modified-date"]["value"] = utils.posix_time_millis()
            self.send_json(test_data, "application/vnd.orcid+json")

    def do_POST(self):
        if self.path == "/0000-0003-4997-3076/works":
            new_work = json.loads(self.get_body_string())
            # TODO: just trust for now; simulate various error conditions
            # later.
            if new_work["bulk"][0]["work"]["title"]["title"]["value"] == "trigger-500":
                self.send_text_error("AN ERROR", status_code=500)
            elif (
                new_work["bulk"][0]["work"]["title"]["title"]["value"] == "trigger-400"
            ):
                error_data = {"user-message": "This is another error"}
                self.send_json_error(error_data, 400, "application/vnd.orcid+json")
            elif (
                new_work["bulk"][0]["work"]["title"]["title"]["value"]
                == "trigger-http-exception"
            ):
                # Note that this assumes the client timeout is < 1 sec. Tests
                # should set the timeout to 0.5sec.
                sleep(1)
                # don't bother with sending data, as the connection
                # will probably be dead by the time this is reached.
            else:
                test_work = load_test_data(TEST_DATA_DIR, "orcid", "work_1526002")
                self.send_json(test_work, "application/vnd.orcid+json")


class MockORCIDAPIWithErrors(MockService):
    def do_GET(self):
        if self.path == "/0000-0003-4997-3076/record":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "profile")
            self.send_json(test_data, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/email":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "email")
            self.send_json(test_data, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "orcid-works-error")
            self.send_json_error(test_data, 500, "application/vnd.orcid+json")

        elif self.path == "/0000-0003-4997-3076/works/1526002":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "orcid-works-error")
            self.send_json_error(test_data, 500, "application/vnd.orcid+json")

        elif self.path == "/trigger-401/record":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "get-profile-401-error")
            self.send_json_error(test_data, 401, "application/vnd.orcid+json")

        elif self.path == "/trigger-415/record":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "get-profile-415-error")
            self.send_json_error(test_data, 415, "application/vnd.orcid+json")

        elif self.path == "/trigger-no-content-type/record":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "profile")
            self.send_json(test_data, None)

        elif self.path == "/trigger-not-json/record":
            test_data = "this is not json!"
            self.send_json_text(test_data, "application/vnd.orcid+json")

        elif self.path == "/trigger-invalid-token/record":
            test_data = load_test_data(
                TEST_DATA_DIR, "orcid", "get-profile-401-error-invalid-token"
            )
            self.send_json_error(test_data, 401, "application/vnd.orcid+json")

        elif self.path == "/trigger-unauthorized/record":
            test_data = load_test_data(
                TEST_DATA_DIR, "orcid", "get-profile-401-error-unauthorized"
            )
            self.send_json_error(test_data, 401, "application/vnd.orcid+json")

        elif self.path == "/trigger-error-some-other/record":
            test_data = load_test_data(
                TEST_DATA_DIR, "orcid", "get-profile-401-error-some-other"
            )
            self.send_json_error(test_data, 401, "application/vnd.orcid+json")

        elif self.path == "/trigger-wrong-content-type/record":
            test_data = load_test_data(
                TEST_DATA_DIR, "orcid", "get-profile-401-error-some-other"
            )
            self.send_json_error(test_data, 401, "application/vnd.orcid+json")

        else:
            # not found!
            test_data = load_test_data(
                TEST_DATA_DIR, "orcid", "get-profile-not-found-error"
            )
            self.send_json_error(test_data, 404, "application/vnd.orcid+json")

    def do_PUT(self):
        if self.path == "/0000-0003-4997-3076/work/1526002":
            test_data = load_test_data(TEST_DATA_DIR, "orcid", "put_work_error")
            self.send_json_error(test_data, 500, "application/vnd.orcid+json")


class MockORCIDOAuth(MockService):
    def do_POST(self):
        if self.path == "/revoke":
            self.send_empty(status_code=200)

        elif self.path == "/token":
            data = parse_qs(self.get_body_string())
            if data["grant_type"] == ["refresh_token"]:
                # TODO: should load the test from our test data file
                # TODO: we should regularize the naming of such files to make it easier
                #       to coordinate them across test code.
                if data["refresh_token"] == ["refresh-token-foo"]:
                    test_data = {
                        "access_token": "access-token-foo-refreshed",
                        "token_type": "bearer",
                        "refresh_token": "refresh-token-foo-refreshed",
                        "expires_in": 631138518,
                        "scope": "/read-limited openid /activities/update",
                        "name": "Foo bar",
                        "orcid": "orcid-id-foo",
                    }
                elif data["refresh_token"] == ["refresh-token-bar"]:
                    test_data = {
                        "access_token": "access-token-bar-refreshed",
                        "token_type": "bearer",
                        "refresh_token": "refresh-token-bar-refreshed",
                        "expires_in": 631138518,
                        "scope": "/read-limited openid /activities/update",
                        "name": "Bar Bear",
                        "orcid": " 0000-1111-2222-3333",
                    }
                else:
                    raise Exception("Sorry, this case not handled")
                self.send_json(test_data, "application/json")
            else:
                if data["code"] == ["foo"]:
                    # TODO: should this be in a file?
                    test_data = {
                        "access_token": "access_token_for_foo",
                        "token_type": "Bearer",
                        "refresh_token": "refresh_token",
                        "expires_in": 1000,
                        "scope": "scope1",
                        "name": "Foo Bear",
                        "orcid": "abc123",
                    }
                    self.send_json(test_data, "application/json")
                elif data["code"] == ["no-content-type"]:
                    self.send(200, {}, None)
                elif data["code"] == ["not-json-content-type"]:
                    self.send(200, {"Content-Type": "foo-son"}, None)
                elif data["code"] == ["error-incorrect-error-format"]:
                    self.send_json_error({"foo": "bar"}, 400, "application/json")
                elif data["code"] == ["error-correct-error-format"]:
                    error = {
                        "error": "some error",
                        "error_description": "a description of some error",
                    }
                    self.send_json_error(error, 400, "application/json")
                elif data["code"] == ["not-json-content"]:
                    self.send_json_text("foo", "application/json")
                else:
                    test_data = {
                        "access_token": "access_token",
                        "token_type": "Bearer",
                        "refresh_token": "refresh_token",
                        "expires_in": 1000,
                        "scope": "scope1",
                        "name": "Foo Bear",
                        "orcid": "abc123",
                    }
                    self.send_json(test_data, "application/json")

    def do_GET(self):
        if self.path == "/authorize":
            # this is a browser-interactive url -
            # worth simulating?
            pass


class MockORCIDOAuth2(MockService):
    def do_POST(self):
        # TODO: Reminder - switch to normal auth2 endpoint in config and here.
        if self.path == "/revoke":
            self.send_empty(status_code=204)
