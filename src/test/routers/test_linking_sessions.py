import contextlib
import json
import urllib

import pytest
from fastapi.testclient import TestClient
from orcidlink.lib import storage_model
from orcidlink.lib.config import config
from orcidlink.main import app
from orcidlink.model_types import LinkRecord
from test.data.utils import load_data_file, load_data_json
from test.mocks.mock_contexts import mock_auth_service, mock_orcid_oauth_service, \
    mock_service_wizard_service, no_stderr

config_yaml = load_data_file('config1.yaml')


@pytest.fixture
def fake_fs(fs):
    fs.create_file("/kb/module/config/config.yaml", contents=config_yaml)
    yield fs


TEST_LINK = load_data_json('link2.json')


@pytest.fixture(autouse=True)
def around_tests(fake_fs):
    config(True)
    yield


def create_link():
    sm = storage_model.storage_model()
    sm.db.links.drop()
    sm.create_link_record(LinkRecord.parse_obj(TEST_LINK))


#
# Canned assertions
#

def assert_create_linking_session(client, authorization: str):
    #
    # Create linking session.
    #
    response = client.post("/linking-sessions",
                           headers={"Authorization": authorization}
                           )

    #
    # Inspect the response for sensible answers.
    #
    assert response.status_code == 201
    session_info = response.json()
    assert isinstance(session_info['session_id'], str)
    return session_info


def assert_get_linking_session(client, session_id: str):
    response = client.get(f"/linking-sessions/{session_id}",
                          headers={"Authorization": "foo"}
                          )

    assert response.status_code == 200
    session_info = response.json()
    session_id = session_info['session_id']
    assert isinstance(session_id, str)
    return session_info


def assert_start_linking_session(client,
                                 session_id: str,
                                 kbase_session: str = None,
                                 kbase_session_backup: str = None,
                                 return_link: str = None,
                                 skip_prompt: str = None):
    headers = {}
    if kbase_session is not None:
        headers['Cookie'] = f"kbase_session={kbase_session}"
    elif kbase_session_backup is not None:
        headers['Cookie'] = f"kbase_session_backup={kbase_session_backup}"

    params = {}
    if return_link is not None:
        params['return_link'] = return_link
    if skip_prompt is not None:
        params['skip_prompt'] = skip_prompt

    # TODO: should be put or post
    response = client.get(f"/linking-sessions/{session_id}/start",
                          headers=headers,
                          params=params,
                          follow_redirects=False
                          )
    assert response.status_code == 302

    # TODO: assertion on the Location for the redirect

    #
    # Get linking session again.
    #
    response = client.get(f"/linking-sessions/{session_id}",
                          headers={"Authorization": "foo"}
                          )

    assert response.status_code == 200
    session_info = response.json()

    assert isinstance(session_info['session_id'], str)
    assert session_info['session_id'] == session_id
    assert 'orcid_auth' not in session_info

    return session_info


def assert_location_params(response, params):
    location = response.headers['location']
    location_url = urllib.parse.urlparse(location)
    location_params = urllib.parse.parse_qs(location_url.query)
    for key, value in params.items():
        assert key in location_params
        assert location_params[key][0] == value


@contextlib.contextmanager
def mock_services():
    with no_stderr():
        with mock_auth_service():
            with mock_service_wizard_service():
                yield


#
# Tests
#


def test_create_linking_session(fake_fs):
    with no_stderr():
        with mock_auth_service():
            client = TestClient(app)
            assert_create_linking_session(client, "foo")


def test_get_linking_session(fake_fs):
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        client = TestClient(app)

        #
        # Create linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id

        # Note that the call will fail if the result does not comply with either
        # LinkingSessionComplete or LinkingSessionInitial

        # The call after creating a linking session will return a LinkingSessionInitial
        # which we only know from the absense of orcid_auth
        assert 'orcid_auth' not in session_info


def test_get_linking_session_errors(fake_fs):
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        client = TestClient(app)

        # Get a non-existent linking session id
        response = client.get(f"/linking-sessions/bar",
                              headers={"Authorization": "foo"})
        assert response.status_code == 404

        # Omit the auth token, expect 401, no auth.
        response = client.get(f"/linking-sessions/bar")
        assert response.status_code == 401

        # Provide a bad auth token, also a 401; i.e., same as no auth
        response = client.get(f"/linking-sessions/bar",
                              headers={"Authorization": "baz"})
        assert response.status_code == 401

        # To get a 403, we need a valid session with a different username.
        session_info = assert_create_linking_session(client, "foo")
        # Provide a bad auth token, also a 401; i.e., same as no auth
        response = client.get(f"/linking-sessions/{session_info['session_id']}",
                              headers={"Authorization": "bar"})
        assert response.status_code == 403


def test_start_linking_session(fake_fs):
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        client = TestClient(app)

        #
        # Create linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id

        # Note that the call will fail if the result does not comply with either
        # LinkingSessionComplete or LinkingSessionInitial

        # The call after creating a linking session will return a LinkingSessionInitial
        # which we only know from the absense of orcid_auth
        assert 'orcid_auth' not in session_info

        #
        # Start the linking session.
        #

        # If we start the linking session, the linking session will be updated, but remain
        #  LinkingSessionInitial
        # assert_start_linking_session(client, initial_session_id, kbase_session="foo")

        # TODO more assertions?

        # return link provided
        assert_start_linking_session(client, initial_session_id, kbase_session="foo", return_link="baz",
                                     skip_prompt="no")
        session_record = assert_get_linking_session(client, initial_session_id)
        assert session_record['return_link'] == "baz"
        assert session_record['skip_prompt'] == "no"

        # skip prompt provided
        # assert_start_linking_session(client, initial_session_id, kbase_session="foo", skip_prompt="yes")
        # session_record = assert_get_linking_session(client, initial_session_id)
        # assert session_record['skip_prompt'] == "yes"


def test_start_linking_session_backup_cookie(fake_fs):
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        client = TestClient(app)

        #
        # Create linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id

        # Note that the call will fail if the result does not comply with either
        # LinkingSessionComplete or LinkingSessionInitial

        # The call after creating a linking session will return a LinkingSessionInitial
        # which we only know from the absense of orcid_auth
        assert 'orcid_auth' not in session_info

        #
        # Start the linking session.
        #

        # If we start the linking session, the linking session will be updated, but remain
        #  LinkingSessionInitial
        # assert_start_linking_session(client, initial_session_id, kbase_session="foo")

        # TODO more assertions?

        # return link provided
        assert_start_linking_session(client, initial_session_id, kbase_session_backup="foo", return_link="baz",
                                     skip_prompt="no")
        session_record = assert_get_linking_session(client, initial_session_id)
        assert session_record['return_link'] == "baz"
        assert session_record['skip_prompt'] == "no"


def test_start_linking_session_errors(fake_fs):
    """
    Now we create a session, and get it back, in order
    to test the "get linking session" call.
    """
    with mock_services():
        client = TestClient(app)

        #
        # Create linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id

        # Note that the call will fail if the result does not comply with either
        # LinkingSessionComplete or LinkingSessionInitial

        # The call after creating a linking session will return a LinkingSessionInitial
        # which we only know from the absense of orcid_auth
        assert 'orcid_auth' not in session_info

        #
        # Start the linking session.
        #

        # If we start the linking session, the linking session will be updated, but remain
        #  LinkingSessionInitial
        # assert_start_linking_session(client, initial_session_id)

        # No auth cookie
        response = client.get(f"/linking-sessions/{initial_session_id}/start",
                              follow_redirects=False
                              )
        assert response.status_code == 401

        # username doesn't  match
        response = client.get(f"/linking-sessions/{initial_session_id}/start",
                              headers={"Cookie": "kbase_session=bar; Path=/"},
                              follow_redirects=False
                              )
        assert response.status_code == 403

        # linking session not found
        response = client.get(f"/linking-sessions/foo/start",
                              headers={"Cookie": "kbase_session=bar; Path=/"},
                              follow_redirects=False
                              )
        assert response.status_code == 404

        # TODO more assertions?


def test_continue_linking_session(fake_fs):
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """

    def assert_continue_linking_session(kbase_session: str = None,
                                        kbase_session_backup: str = None,
                                        return_link: str = None,
                                        skip_prompt: str = None):
        client = TestClient(app)

        #
        # Create linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id

        # Note that the call will fail if the result does not comply with either
        # LinkingSessionComplete or LinkingSessionInitial

        # The call after creating a linking session will return a LinkingSessionInitial
        # which we only know from the absense of orcid_auth
        assert 'orcid_auth' not in session_info

        #
        # Start the linking session.
        #

        # If we start the linking session, the linking session will be updated, but remain
        #  LinkingSessionInitial
        assert_start_linking_session(client, initial_session_id, kbase_session="foo", return_link=return_link,
                                     skip_prompt=skip_prompt)

        #
        # In the actual OAuth flow, the browser would invoke the start link endpoint
        # above, and naturally follow the redirect to ORCID OAuth.
        # We can't do that here, but we can simulate it via the mock oauth
        # service. That service also has a non-interactive endpoint "/authorize"
        # which exchanges the code for an access_token (amongst other things)
        #
        params = {
            'code': 'foo',
            'state': json.dumps({
                'session_id': initial_session_id
            })
        }

        headers = {}
        if kbase_session is not None:
            headers['Cookie'] = f"kbase_session={kbase_session}"
        if kbase_session_backup is not None:
            headers['Cookie'] = f"kbase_session_backup={kbase_session_backup}"

        response = client.get("/continue-linking-session",
                              headers=headers,
                              params=params,
                              follow_redirects=False)
        assert response.status_code == 302

        # TODO assertions about Location

        #
        # Get the session info post-continuation, which will complete the
        # ORCID OAuth.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        assert session_info['session_id'] == initial_session_id
        assert 'orcid_auth' in session_info

        #
        # Finish the linking session
        #
        response = client.put(f"/linking-sessions/{initial_session_id}/finish",
                              headers={'Authorization': "foo"})
        assert response.status_code == 200

        # TODO more assertions?

    # Use individual context managers here, as we only need this
    # setup once. If we need to use it again, we can can it in a
    # function above.
    with no_stderr():
        with mock_auth_service():
            with mock_service_wizard_service():
                with mock_orcid_oauth_service():
                    assert_continue_linking_session(kbase_session="foo", skip_prompt="no")
                    assert_continue_linking_session(kbase_session_backup="foo", skip_prompt="no")
                    assert_continue_linking_session(kbase_session="foo", return_link="bar", skip_prompt="no")


def test_continue_linking_session_errors(fake_fs):
    """
    Here we simulate the oauth flow with ORCID - in which
    we redirect the browser to ORCID, which ends up returning
    to our return url which in turn may ask the user to confirm
    the linking, after which we exchange the code for an access token.
    """
    with no_stderr():
        with mock_auth_service():
            with mock_service_wizard_service():
                with mock_orcid_oauth_service():
                    client = TestClient(app)

                    #
                    # Create linking session.
                    #
                    initial_session_info = assert_create_linking_session(client, "foo")
                    initial_session_id = initial_session_info['session_id']

                    #
                    # Get the session info.
                    #
                    session_info = assert_get_linking_session(client, initial_session_id)
                    assert session_info['session_id'] == initial_session_id

                    # Note that the call will fail if the result does not comply with either
                    # LinkingSessionComplete or LinkingSessionInitial

                    # The call after creating a linking session will return a LinkingSessionInitial
                    # which we only know from the absense of orcid_auth
                    assert 'orcid_auth' not in session_info

                    #
                    # Start the linking session.
                    #

                    # If we start the linking session, the linking session will be updated, but remain
                    #  LinkingSessionInitial
                    assert_start_linking_session(client, initial_session_id, kbase_session="foo", skip_prompt="yes")

                    #
                    # In the actual OAuth flow, the browser would invoke the start link endpoint
                    # above, and naturally follow the redirect to ORCID OAuth.
                    # We can't do that here, but we can simulate it via the mock oauth
                    # service. That service also has a non-interactive endpoint "/authorize"
                    # which exchanges the code for an access_token (amongst other things)
                    #
                    params = {
                        'code': 'foo',
                        'state': json.dumps({
                            'session_id': initial_session_id
                        })
                    }

                    # response = client.get(f"/continue-linking-session",
                    #                       headers={
                    #                           "Cookie": "kbase_session=foo"
                    #                       },
                    #                       params=params,
                    #                       follow_redirects=False)
                    # assert response.status_code == 302

                    # No auth cookie: no kbase_session or kbase_session_backup
                    response = client.get(f"/continue-linking-session",
                                          params=params,
                                          follow_redirects=False)
                    assert response.status_code == 401

                    # Error returned from orcid
                    # TODO: double check the ORCID error structure; here we assume it is a string.
                    params = {
                        'error': 'foo'
                    }
                    response = client.get(f"/continue-linking-session",
                                          headers={
                                              "Cookie": "kbase_session=foo"
                                          },
                                          params=params,
                                          follow_redirects=False)
                    assert response.status_code == 302
                    # TODO: test the response Location and the location info.

                    # No code
                    params = {
                        'state': json.dumps({
                            'session_id': initial_session_id
                        })
                    }
                    response = client.get(f"/continue-linking-session",
                                          headers={
                                              "Cookie": "kbase_session=foo"
                                          },
                                          params=params,
                                          follow_redirects=False)
                    assert response.status_code == 302
                    assert_location_params(response, {
                        'code': 'link.code_missing',
                        'title': 'Linking code missing',
                        'message': "The 'code' query param is required but missing"
                    })

                    # No state
                    params = {
                        'code': 'foo'
                    }
                    response = client.get(f"/continue-linking-session",
                                          headers={
                                              "Cookie": "kbase_session=foo"
                                          },
                                          params=params,
                                          follow_redirects=False)
                    assert response.status_code == 302
                    assert_location_params(response, {
                        'code': 'link.state_missing',
                        'title': 'Linking state missing',
                        'message': "The 'state' query param is required but missing"
                    })

                    # No session_id
                    params = {
                        'code': 'foo',
                        'state': json.dumps({
                        })
                    }
                    response = client.get(f"/continue-linking-session",
                                          headers={
                                              "Cookie": "kbase_session=foo"
                                          },
                                          params=params,
                                          follow_redirects=False)
                    assert response.status_code == 302
                    assert_location_params(response, {
                        'code': 'link.session_id_missing',
                        'title': 'Linking Error',
                        'message': "The 'session_id' was not provided in the 'state' query param"
                    })


def test_delete_linking_session(fake_fs):
    with mock_services():
        client = TestClient(app)

        #
        # Create the linking session.
        #
        initial_session_info = assert_create_linking_session(client, "foo")
        initial_session_id = initial_session_info['session_id']

        #
        # Get the session info.
        #
        session_info = assert_get_linking_session(client, initial_session_id)
        session_id = session_info['session_id']
        assert session_id == initial_session_id

        #
        # Delete the session
        #
        response = client.delete(f"/linking-sessions/{session_id}",
                                 headers={"Authorization": "foo"})
        assert response.status_code == 204

        #
        # Check if it exists.
        #
        with pytest.raises(Exception) as ex:
            assert_get_linking_session(client, initial_session_id)
        assert ex is not None

# def xest_get_link(fake_fs):
#     server = MockServer("127.0.0.1", MockAuthService)
#     server.start_service()
#     # hack the config
#     config.set_config(["kbase", "services", "Auth2", "url"],
#                       f"{server.base_url()}/services/auth/api/V2/token",
#                       reload=True)
#
#     client = TestClient(app)
#     # client.headers['authorization'] = 'foo'
#     response = client.get("/link",
#                           headers={"Authorization": "foo"}
#                           )
#     assert response.status_code == 200
#
#     response = client.get("/link",
#                           headers={"Authorization": "foox"}
#                           )
#     assert response.status_code == 401
#
#     response = client.get("/link",
#                           headers={"Authorization": "bar"}
#                           )
#     assert response.status_code == 404


# def xest_is_linked(fake_fs):
#     server = MockServer("127.0.0.1", MockAuthService)
#     server.start_service()
#     # hack the config
#     config.set_config(["kbase", "services", "Auth2", "url"],
#                       f"{server.base_url()}/services/auth/api/V2/token",
#                       reload=True)
#
#     client = TestClient(app)
#     # client.headers['authorization'] = 'foo'
#     response = client.get("/link/is_linked",
#                           headers={"Authorization": "foo"}
#                           )
#     result = response.json()
#     assert result is True
#
#     response = client.get("/link/is_linked",
#                           headers={"Authorization": "bar"}
#                           )
#     result = response.json()
#     assert result is False
#
#     response = client.get("/link/is_linked",
#                           headers={"Authorization": "baz"}
#                           )
#     assert response.status_code == 401


# def xest_delete_link(fake_fs):
#     mock_auth_service = MockServer("127.0.0.1", MockAuthService)
#     mock_auth_service.start_service()
#     mock_orcid_oauth_service = MockServer("127.0.0.1", MockORCIDOAuth)
#     mock_orcid_oauth_service.start_service()
#     try:
#         # hack the config
#         config.set_config(["kbase", "services", "Auth2", "url"],
#                           f"{mock_auth_service.base_url()}/services/auth/api/V2/token",
#                           reload=True)
#         config.set_config(["orcid", "oauthBaseURL"],
#                           f"{mock_orcid_oauth_service.base_url()}")
#
#         client = TestClient(app)
#         # client.headers['authorization'] = 'foo'
#
#         response = client.delete("/link",
#                                  headers={"Authorization": "foo"}
#                                  )
#         assert response.status_code == 204
#
#         response = client.delete("/link",
#                                  headers={"Authorization": "bar"}
#                                  )
#         assert response.status_code == 204
#     finally:
#         mock_auth_service.stop_service()
#         mock_orcid_oauth_service.stop_service()
