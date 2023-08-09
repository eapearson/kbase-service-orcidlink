import contextlib
import json
from urllib.parse import urlparse, parse_qs
from test.mocks.data import load_data_file, load_data_json
from test.mocks.env import MOCK_KBASE_SERVICES_PORT, MOCK_ORCID_OAUTH_PORT, TEST_ENV
from test.mocks.mock_contexts import (
    mock_auth_service,
    mock_orcid_oauth_service,
    no_stderr,
)
from test.mocks.testing_utils import TOKEN_BAR, TOKEN_FOO, clear_storage_model

import os
from unittest import mock
import pytest
from fastapi.testclient import TestClient

from orcidlink.lib import utils
from orcidlink.lib.config import Config2
from orcidlink.main import app
from orcidlink.model import LinkRecord
from orcidlink.storage.storage_model import storage_model
from test.routers.orcid.test_works import MOCK_ORCID_API_PORT


TEST_LINK = load_data_json("link2.json")
TEST_LINK1 = load_data_json("link1.json")


def create_link(link_data):
    sm = storage_model()
    sm.create_link_record(LinkRecord.model_validate(link_data))


#
# Canned assertions
#


def assert_create_linking_session(client, authorization: str):
    #
    # Create linking session.
    #
    clear_storage_model()
    response = client.post(
        "/linking-sessions", headers={"Authorization": authorization}
    )

    #
    # Inspect the response for sensible answers.
    #
    assert response.status_code == 201
    session_info = response.json()
    assert isinstance(session_info["session_id"], str)
    return session_info


def assert_get_linking_session(client, session_id: str):
    response = client.get(
        f"/linking-sessions/{session_id}", headers={"Authorization": TOKEN_FOO}
    )

    assert response.status_code == 200
    session_info = response.json()
    session_id = session_info["session_id"]
    assert isinstance(session_id, str)
    return session_info


def assert_start_linking_session(
    client,
    session_id: str,
    kbase_session: str | None = None,
    kbase_session_backup: str | None = None,
    return_link: str | None = None,
    skip_prompt: str | None = None,
):
    headers = {}
    if kbase_session is not None:
        headers["Cookie"] = f"kbase_session={kbase_session}"
    elif kbase_session_backup is not None:
        headers["Cookie"] = f"kbase_session_backup={kbase_session_backup}"

    params = {}
    if return_link is not None:
        params["return_link"] = return_link
    if skip_prompt is not None:
        params["skip_prompt"] = skip_prompt

    # TODO: should be put or post
    response = client.get(
        f"/linking-sessions/{session_id}/oauth/start",
        headers=headers,
        params=params,
        follow_redirects=False,
    )
    assert response.status_code == 302

    # # TODO: assertion on the Location for the redirect

    # #
    # # Get linking session again.
    # #
    # response = client.get(
    #     f"/linking-sessions/{session_id}", headers={"Authorization": kbase_session}
    # )

    # assert response.status_code == 200
    # session_info = response.json()

    # assert isinstance(session_info["session_id"], str)
    # assert session_info["session_id"] == session_id
    # assert session_info["kind"] == "started"
    # assert "orcid_auth" not in session_info

    # return session_info


def assert_continue_linking_session(
    client,
    session_id: str,
    kbase_session: str | None = None,
    expected_response_code: int | None = None,
):
    # FINISH
    #
    # Get linking session again.
    #

    params = {
        "code": "foo",
        "state": json.dumps({"session_id": session_id}),
    }

    headers = {}
    headers["Cookie"] = f"kbase_session={kbase_session}"

    response = client.get(
        "/linking-sessions/oauth/continue",
        headers=headers,
        params=params,
        follow_redirects=False,
    )
    assert response.status_code == expected_response_code

    # response = client.put(
    #     f"/linking-sessions/{session_id}/finish",
    #     headers={"Authorization": kbase_session},
    # )
    # assert response.status_code == 200


def assert_finish_linking_session(
    client,
    session_id: str,
    kbase_session: str | None = None,
    expected_response_code: int = 200,
):
    # FINISH
    #
    # Get linking session again.
    #
    response = client.put(
        f"/linking-sessions/{session_id}/finish",
        headers={"Authorization": kbase_session},
    )
    assert response.status_code == expected_response_code

    # response = client.get(
    #     f"/linking-sessions/{session_id}", headers={"Authorization": TOKEN_FOO}
    # )

    # assert response.status_code == 200
    # session_info = response.json()

    # assert isinstance(session_info["session_id"], str)
    # assert session_info["session_id"] == session_id
    # assert session_info["kind"] == "started"
    # assert "orcid_auth" not in session_info

    # return session_info


def assert_location_params(response, params):
    location = response.headers["location"]
    location_url = urlparse(location)
    location_params = parse_qs(location_url.query)
    for key, value in params.items():
        assert key in location_params
        assert location_params[key][0] == value


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service(MOCK_KBASE_SERVICES_PORT):
            yield


#
# Tests
#


def test_create_linking_session():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            clear_storage_model()
            client = TestClient(app)
            assert_create_linking_session(client, TOKEN_FOO)


def test_create_linking_session_already_linked():
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            #
            #
            #
            clear_storage_model()

            #
            # Create a link for user "foo"
            #
            create_link(TEST_LINK1)

            #
            # Create linking session; this should fail with errors.AlreadyLinkedError
            #
            client = TestClient(app)
            response = client.post(
                "/linking-sessions", headers={"Authorization": TOKEN_FOO}
            )

            #
            # Inspect the response for sensible answers.
            #
            assert response.status_code == 400

            # session_info = response.json()
            # assert isinstance(session_info["session_id"], str)
            # return session_info


def test_get_linking_session():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        with mock.patch.dict(os.environ, TEST_ENV, clear=True):
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                client = TestClient(app)

                clear_storage_model()

                #
                # Create linking session.
                #
                initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
                initial_session_id = initial_session_info["session_id"]

                assert_start_linking_session(
                    client,
                    initial_session_id,
                    kbase_session=TOKEN_FOO,
                    kbase_session_backup=TOKEN_FOO,
                    return_link="baz",
                    skip_prompt="no",
                )

                assert_continue_linking_session(
                    client,
                    initial_session_id,
                    TOKEN_FOO,
                    expected_response_code=302,
                )

                # assert_finish_linking_session(
                #     client,
                #     initial_session_id,
                #     TOKEN_FOO,
                #     expected_response_code=200,
                # )

                response = client.get(
                    f"/linking-sessions/{initial_session_id}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 200

                # TODO: assert more stuff about the response?

                # linking_session = client.get_linking_session(initial_session_id)
                # assert linking_session["session_id"] == initial_session_id

                # initial_session_id = initial_session_info["session_id"]

                #
                # Get the session info.
                #
                # session_info = assert_get_linking_session(client, initial_session_id)
                # assert session_info["session_id"] == initial_session_id

                # Note that the call will fail if the result does not comply with either
                # LinkingSessionComplete or LinkingSessionInitial

                # The call after creating a linking session will return a LinkingSessionInitial
                # which we only know from the absense of orcid_auth
                # assert "orcid_auth" not in initial_session_info


def test_delete_linking_session():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                client = TestClient(app)

                clear_storage_model()

                #
                # Create linking session.
                #
                initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
                initial_session_id = initial_session_info["session_id"]

                assert_start_linking_session(
                    client,
                    initial_session_id,
                    kbase_session=TOKEN_FOO,
                    kbase_session_backup=TOKEN_FOO,
                    return_link="baz",
                    skip_prompt="no",
                )

                assert_continue_linking_session(
                    client,
                    initial_session_id,
                    TOKEN_FOO,
                    expected_response_code=302,
                )

                # assert_finish_linking_session(
                #     client,
                #     initial_session_id,
                #     TOKEN_FOO,
                #     expected_response_code=200,
                # )

                response = client.get(
                    f"/linking-sessions/{initial_session_id}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 200

                response = client.delete(
                    f"/linking-sessions/{initial_session_id}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 204

                response = client.get(
                    f"/linking-sessions/{initial_session_id}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 404

                # TODO: assert more stuff about the response?

                # linking_session = client.get_linking_session(initial_session_id)
                # assert linking_session["session_id"] == initial_session_id

                # initial_session_id = initial_session_info["session_id"]

                #
                # Get the session info.
                #
                # session_info = assert_get_linking_session(client, initial_session_id)
                # assert session_info["session_id"] == initial_session_id

                # Note that the call will fail if the result does not comply with either
                # LinkingSessionComplete or LinkingSessionInitial

                # The call after creating a linking session will return a LinkingSessionInitial
                # which we only know from the absense of orcid_auth
                # assert "orcid_auth" not in initial_session_info


def test_get_linking_session_errors():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                client = TestClient(app)

                clear_storage_model()

                # Get a non-existent linking session id
                response = client.get(
                    f"/linking-sessions/{'x' * 36}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 404

                # Get a malformed linking session id
                response = client.get(
                    "/linking-sessions/bar", headers={"Authorization": TOKEN_FOO}
                )
                assert response.status_code == 422

                # Omit the auth token, expect 422, not 401, since the
                # authorization header is a required input to the endpoint.
                response = client.get(f"/linking-sessions/{'x' * 36}")
                assert response.status_code == 422
                response = client.get(
                    f"/linking-sessions/{'x' * 36}", headers={"Authorization": "baz"}
                )
                assert response.status_code == 422

                # Should also be 404, because it is not completed yet.
                session_info = assert_create_linking_session(client, TOKEN_FOO)
                response = client.get(
                    f"/linking-sessions/{session_info['session_id']}",
                    headers={"Authorization": TOKEN_FOO},
                )
                assert response.status_code == 404

                # To get a 403, we need a valid session with a different username.

                assert_start_linking_session(
                    client,
                    session_info["session_id"],
                    kbase_session=TOKEN_FOO,
                    kbase_session_backup=TOKEN_FOO,
                    return_link="baz",
                    skip_prompt="no",
                )

                assert_continue_linking_session(
                    client,
                    session_info["session_id"],
                    TOKEN_BAR,
                    expected_response_code=403,
                )

                assert_continue_linking_session(
                    client,
                    session_info["session_id"],
                    TOKEN_FOO,
                    expected_response_code=302,
                )

                assert_finish_linking_session(
                    client,
                    session_info["session_id"],
                    TOKEN_BAR,
                    expected_response_code=403,
                )

                # # session_info = assert_create_linking_session(client, TOKEN_FOO)
                # # Provide a bad auth token, also a 401; i.e., same as no auth
                # response = client.get(
                #     f"/linking-sessions/{session_info['session_id']}",
                #     headers={"Authorization": TOKEN_BAR},
                # )
                # assert response.status_code == 403


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_start_linking_session():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                client = TestClient(app)

                clear_storage_model()

                #
                # Create linking session.
                #
                initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
                initial_session_id = initial_session_info["session_id"]

                # #
                # # Get the session info.
                # #
                # session_info = assert_get_linking_session(client, initial_session_id)
                # assert session_info["session_id"] == initial_session_id

                # # Note that the call will fail if the result does not comply with either
                # # LinkingSessionComplete or LinkingSessionInitial

                # # The call after creating a linking session will return a LinkingSessionInitial
                # # which we only know from the absense of orcid_auth
                # assert "orcid_auth" not in session_info

                #
                # Start the linking session.
                #

                # return link provided
                assert_start_linking_session(
                    client,
                    initial_session_id,
                    kbase_session=TOKEN_FOO,
                    return_link="baz",
                    skip_prompt="no",
                )
                # session_record = assert_get_linking_session(client, initial_session_id)
                # assert started_session["return_link"] == "baz"
                # assert started_session["skip_prompt"] == "no"

                # skip prompt provided
                # assert_start_linking_session(client, initial_session_id, kbase_session="foo", skip_prompt="yes")
                # session_record = assert_get_linking_session(client, initial_session_id)
                # assert session_record['skip_prompt'] == "yes"


def test_start_linking_session_backup_cookie():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                client = TestClient(app)

                clear_storage_model()

                #
                # Create linking session.
                #
                initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
                initial_session_id = initial_session_info["session_id"]

                assert_start_linking_session(
                    client,
                    initial_session_id,
                    kbase_session_backup=TOKEN_FOO,
                    return_link="baz",
                    skip_prompt="no",
                )


def test_start_linking_session_errors():
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):
        with mock_services():
            client = TestClient(app)

            clear_storage_model()

            #
            # Create linking session.
            #
            initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
            initial_session_id = initial_session_info["session_id"]

            #
            # Get the session info.
            #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id

            # Note that the call will fail if the result does not comply with either
            # LinkingSessionComplete or LinkingSessionInitial

            # The call after creating a linking session will return a LinkingSessionInitial
            # which we only know from the absense of orcid_auth
            assert "orcid_auth" not in initial_session_info

            #
            # Start the linking session.
            #

            # If we start the linking session, the linking session will be updated, but remain
            #  LinkingSessionInitial
            # assert_start_linking_session(client, initial_session_id)

            # No auth cookie
            response = client.get(
                f"/linking-sessions/{initial_session_id}/oauth/start",
                follow_redirects=False,
            )
            assert response.status_code == 401

            # username doesn't  match
            response = client.get(
                f"/linking-sessions/{initial_session_id}/oauth/start",
                headers={"Cookie": "kbase_session=bar; Path=/"},
                follow_redirects=False,
            )
            assert response.status_code == 403

            # linking session id not correct format (s.b. 36 characters)
            response = client.get(
                "/linking-sessions/foo/oauth/start",
                headers={"Cookie": "kbase_session=bar; Path=/"},
                follow_redirects=False,
            )
            assert response.status_code == 422

            # linking session not found
            response = client.get(
                f"/linking-sessions/{'x' * 36}/oauth/start",
                headers={"Cookie": "kbase_session=bar; Path=/"},
                follow_redirects=False,
            )
            assert response.status_code == 404

            # TODO more assertions?


# @mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_continue_linking_session():
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """
    with mock.patch.dict(os.environ, TEST_ENV, clear=True):

        def assert_continue_linking_session(
            kbase_session: str | None = None,
            kbase_session_backup: str | None = None,
            return_link: str | None = None,
            skip_prompt: str | None = None,
            expected_response_code: int | None = None,
        ):
            client = TestClient(app)

            #
            # Create linking session.
            #
            initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
            initial_session_id = initial_session_info["session_id"]

            #
            # Get the session info.
            # #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id

            # Note that the call will fail if the result does not comply with either
            # LinkingSessionComplete or LinkingSessionInitial

            # The call after creating a linking session will return a LinkingSessionInitial
            # which we only know from the absence of orcid_auth
            assert "orcid_auth" not in initial_session_info

            #
            # Start the linking session.
            #

            # If we start the linking session, the linking session will be updated, but remain
            #  LinkingSessionInitial
            assert_start_linking_session(
                client,
                initial_session_id,
                kbase_session=TOKEN_FOO,
                return_link=return_link,
                skip_prompt=skip_prompt,
            )

            #
            # In the actual OAuth flow, the browser would invoke the start link endpoint
            # above, and naturally follow the redirect to ORCID OAuth.
            # We can't do that here, but we can simulate it via the mock oauth
            # service. That service also has a non-interactive endpoint "/authorize"
            # which exchanges the code for an access_token (amongst other things)
            #
            params = {
                "code": "foo",
                "state": json.dumps({"session_id": initial_session_id}),
            }

            headers = {}
            if kbase_session is not None:
                headers["Cookie"] = f"kbase_session={kbase_session}"
            if kbase_session_backup is not None:
                headers["Cookie"] = f"kbase_session_backup={kbase_session_backup}"

            response = client.get(
                "/linking-sessions/oauth/continue",
                headers=headers,
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == expected_response_code

            # TODO assertions about Location

            #
            # Get the session info post-continuation, which will complete the
            # ORCID OAuth.
            #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert started_linking_session["session_id"] == initial_session_id
            # # session_info is not in the public session info
            # assert "orcid_auth" in started_linking_session
            # TODO: test that it is in the raw session info, though.

            #
            # Finish the linking session
            #
            response = client.put(
                f"/linking-sessions/{initial_session_id}/finish",
                headers={"Authorization": TOKEN_FOO},
            )
            assert response.status_code == 200

            # TODO more assertions?

        # Use individual context managers here, as we only need this
        # setup once. If we need to use it again, we can can it in a
        # function above.
        with mock_services():
            with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
                clear_storage_model()

                assert_continue_linking_session(
                    kbase_session=TOKEN_FOO,
                    skip_prompt="no",
                    expected_response_code=302,
                )
                clear_storage_model()
                assert_continue_linking_session(
                    kbase_session_backup=TOKEN_FOO,
                    skip_prompt="no",
                    expected_response_code=302,
                )
                clear_storage_model()
                assert_continue_linking_session(
                    kbase_session=TOKEN_FOO,
                    return_link="bar",
                    skip_prompt="no",
                    expected_response_code=302,
                )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_continue_linking_session_errors():
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            client = TestClient(app)
            clear_storage_model()

            #
            # Create linking session.
            #
            initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
            initial_session_id = initial_session_info["session_id"]

            #
            # Get the session info.
            # #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id

            # Note that the call will fail if the result does not comply with either
            # LinkingSessionComplete or LinkingSessionInitial

            # The call after creating a linking session will return a LinkingSessionInitial
            # which we only know from the absense of orcid_auth
            assert "orcid_auth" not in initial_session_info

            #
            # Start the linking session.
            #

            # If we start the linking session, the linking session will be updated, but remain
            # LinkingSessionInitial
            assert_start_linking_session(
                client,
                initial_session_id,
                kbase_session=TOKEN_FOO,
                skip_prompt="yes",
            )

            #
            # In the actual OAuth flow, the browser would invoke the start link endpoint
            # above, and naturally follow the redirect to ORCID OAuth.
            # We can't do that here, but we can simulate it via the mock oauth
            # service. That service also has a non-interactive endpoint "/authorize"
            # which exchanges the code for an access_token (amongst other things)
            #
            params = {
                "code": "foo",
                "state": json.dumps({"session_id": initial_session_id}),
            }

            # No auth cookie: no kbase_session or kbase_session_backup
            response = client.get(
                "/linking-sessions/oauth/continue",
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 401

            # Error returned from orcid
            # TODO: double check the ORCID error structure; here we assume it is a string.
            params = {"error": "foo"}
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers={"Cookie": f"kbase_session={TOKEN_FOO}"},
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 302
            # TODO: test the response Location and the location info.

            # No code
            params = {"state": json.dumps({"session_id": initial_session_id})}
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers={"Cookie": f"kbase_session={TOKEN_FOO}"},
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 302
            assert_location_params(
                response,
                {
                    "code": "link.code_missing",
                    "title": "Linking code missing",
                    "message": "The 'code' query param is required but missing",
                },
            )

            # No state
            params = {"code": "foo"}
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers={"Cookie": f"kbase_session={TOKEN_FOO}"},
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 302
            assert_location_params(
                response,
                {
                    "code": "link.state_missing",
                    "title": "Linking state missing",
                    "message": "The 'state' query param is required but missing",
                },
            )

            # No session_id
            params = {"code": "foo", "state": json.dumps({})}
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers={"Cookie": f"kbase_session={TOKEN_FOO}"},
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 302
            assert_location_params(
                response,
                {
                    "code": "link.session_id_missing",
                    "title": "Linking Error",
                    "message": "The 'session_id' was not provided in the 'state' query param",
                },
            )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_continue_linking_session_error_already_continued():
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            client = TestClient(app)

            clear_storage_model()

            #
            # Create linking session.
            #
            initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
            initial_session_id = initial_session_info["session_id"]

            #
            # Get the session info.
            #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id

            # Note that the call will fail if the result does not comply with either
            # LinkingSessionComplete or LinkingSessionInitial

            # The call after creating a linking session will return a LinkingSessionInitial
            # which we only know from the absense of orcid_auth
            assert "orcid_auth" not in initial_session_info

            #
            # Start the linking session.
            #

            # If we start the linking session, the linking session will be updated, but remain
            # LinkingSessionInitial
            assert_start_linking_session(
                client,
                initial_session_id,
                kbase_session=TOKEN_FOO,
                skip_prompt="yes",
            )

            #
            # In the actual OAuth flow, the browser would invoke the start link endpoint
            # above, and naturally follow the redirect to ORCID OAuth.
            # We can't do that here, but we can simulate it via the mock oauth
            # service. That service also has a non-interactive endpoint "/authorize"
            # which exchanges the code for an access_token (amongst other things)
            #
            params = {
                "code": "foo",
                "state": json.dumps({"session_id": initial_session_id}),
            }

            headers = {
                "Cookie": f"kbase_session={TOKEN_FOO}",
            }

            # First time, it should be fine, returning a 302 as expected, with a
            # location to ORCID
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers=headers,
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 302

            # Second time it should produce an error
            response = client.get(
                "/linking-sessions/oauth/continue",
                headers=headers,
                params=params,
                follow_redirects=False,
            )
            assert response.status_code == 404
            # TODO: should be a 302, redirected to the error page.
            # assert response.status_code == 302
            # assert_location_params(
            #     response,
            #     {
            #         "code": "linking_session.wrong_state",
            #         "title": "Linking Error",
            #         "message": "The session is not in 'started' state",
            #     },
            # )


@mock.patch.dict(os.environ, TEST_ENV, clear=True)
def test_finish_linking_session_error_already_finished():
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """
    with mock_services():
        with mock_orcid_oauth_service(MOCK_ORCID_OAUTH_PORT):
            client = TestClient(app)

            clear_storage_model()

            #
            # Create linking session.
            #
            initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
            initial_session_id = initial_session_info["session_id"]

            #
            # Get the session info.
            #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id

            # Note that the call will fail if the result does not comply with either
            # LinkingSessionComplete or LinkingSessionInitial

            # The call after creating a linking session will return a LinkingSessionInitial
            # which we only know from the absense of orcid_auth
            assert "orcid_auth" not in initial_session_info

            #
            # If we try to finish before starting, we should get a 400 error
            #
            response = client.put(
                f"/linking-sessions/{initial_session_id}/finish",
                headers={"Authorization": TOKEN_FOO},
            )
            assert response.status_code == 404

            # # "invalidState",
            # # "Invalid Linking Session State",
            # # "The linking session must be in 'complete' state, but is not",
            # assert response.json() == {
            #     "code": "notFound",
            #     "title": "Not Found",
            #     "message": "Linking session not found",
            # }

            # #
            # # Start the linking session.
            # #

            # # If we start the linking session, the linking session will be updated, but remain
            # # LinkingSessionInitial
            # assert_start_linking_session(
            #     client,
            #     initial_session_id,
            #     kbase_session=TOKEN_FOO,
            #     skip_prompt="yes",
            # )

            # #
            # # In the actual OAuth flow, the browser would invoke the start link endpoint
            # # above, and naturally follow the redirect to ORCID OAuth.
            # # We can't do that here, but we can simulate it via the mock oauth
            # # service. That service also has a non-interactive endpoint "/authorize"
            # # which exchanges the code for an access_token (amongst other things)
            # #
            # params = {
            #     "code": "foo",
            #     "state": json.dumps({"session_id": initial_session_id}),
            # }

            # headers = {
            #     "Cookie": f"kbase_session={TOKEN_FOO}",
            # }

            # # First time, it should be fine, returning a 302 as expected, with a
            # # location to ORCID
            # response = client.get(
            #     "/linking-sessions/oauth/continue",
            #     headers=headers,
            #     params=params,
            #     follow_redirects=False,
            # )
            # assert response.status_code == 302

            # #
            # # Get the session info post-continuation, which will complete the
            # # ORCID OAuth.
            # #
            # session_info = assert_get_linking_session(client, initial_session_id)
            # assert session_info["session_id"] == initial_session_id
            # # The api should not reveal the orcid_auth
            # assert session_info["kind"] == "complete"
            # assert "orcid_auth" in session_info

            # #
            # # Finish the linking session; first time, ok.
            # #
            # response = client.put(
            #     f"/linking-sessions/{initial_session_id}/finish",
            #     headers={"Authorization": TOKEN_FOO},
            # )
            # assert response.status_code == 200

            # # Second time it should produce a 404 since it will have been deleted!
            # response = client.put(
            #     f"/linking-sessions/{initial_session_id}/finish",
            #     headers={"Authorization": TOKEN_FOO},
            # )
            # assert response.status_code == 404


# TODO: revive this.
# Need to get the linking session all the way to completed.
# def xest_delete_linking_session(fake_fs):
#     with mock_services():
#         client = TestClient(app)

#         #
#         # Create the linking session.
#         #
#         initial_session_info = assert_create_linking_session(client, TOKEN_FOO)
#         initial_session_id = initial_session_info["session_id"]

#         #
#         # Get the session info.
#         #
#         # session_info = assert_get_linking_session(client, initial_session_id)
#         # session_id = session_info["session_id"]
#         # assert session_id == initial_session_id

#         #
#         # Delete the session
#         #
#         response = client.delete(
#             f"/linking-sessions/{initial_session_id}", headers={"Authorization": TOKEN_FOO}
#         )
#         assert response.status_code == 204

#         #
#         # Check if it exists.
#         #
#         with pytest.raises(Exception) as ex:
#             assert_get_linking_session(client, initial_session_id)
#         assert ex is not None
