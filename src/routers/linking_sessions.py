import json
import uuid
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, HTTPException, Header, responses
from lib.auth import get_username
from lib.config import get_config, get_service_uri
from lib.constants import LINKING_SESSION_TTL, ORCID_SCOPES
from lib.responses import ui_error_response
from lib.storage_model import StorageModel
from lib.utils import current_time_millis
from pydantic import BaseModel, Field

from src.model_types import LinkingSessionComplete, SessionInfo, SimpleSuccess

router = APIRouter(
    responses={404: {"description": "Not found"}}
)


##
# This is a convenience
#
def get_linking_session_record(session_id, authorization):
    model = StorageModel()
    session_record = model.get_linking_session(session_id)

    if session_record is None:
        raise HTTPException(404, 'Linking session not found')

    if authorization is not None:
        if not session_record['kbase_auth_token'] == authorization:
            raise HTTPException(403, 'Authorization does not match linking session')

    return session_record


#
# Redirection target for linking.
#
# The provided "code" is very short-lived and must be exchanged for the
# long-lived tokens without allowing the user to dawdle over it.
#
# Yet we do want the user to verify the linking with full account info first.
# Even using the forced logout during ORCID authentication, the ORCID interface
# does not identify the account after login. Since their user ids are cryptic,
#
# it would be possible on a multi-user computer to use the wrong ORCID Id.
# So what we do is save the response and issue our own temporary token.
# Upon submitting that token to /finish-link link is made.
#
@router.get("/continue-linking-session", responses={
    302: {
        "description": "Redirect to the continuation page; or error page"
    }
})
async def continue_linking_session(
        code: str | None = None,
        state: str | None = None,
        error: str | None = None
):
    # Note that this is the target for redirection from ORCID,
    # and we don't have an Authorization header and we don't
    # (necessarily) have an auth cookie.
    # So we use the state to get the session id.

    if error is not None:
        return ui_error_response("link.orcid_error",
                                 "ORCID Error Linking",
                                 error)

    if code is None:
        return ui_error_response("link.code_missing",
                                 "Linking code missing",
                                 "The 'code' query param is required but missing")

    if state is None:
        return ui_error_response("link.state_missing",
                                 "Linking Error",
                                 "The 'state' query param is required but missing")

    unpacked_state = json.loads(state)

    if 'session_id' not in unpacked_state:
        return ui_error_response("link.session_id_missing",
                                 "Linking Error",
                                 "The 'session_id' was not provided in the 'state' query param")

    session_id = unpacked_state.get("session_id")

    session_record = get_linking_session_record(session_id, None)

    #
    # Exchange the temporary token from ORCID for the authorized token.
    #
    header = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    # Note that the redirect uri below is just for the api - it is not actually used
    # for redirection in this case.
    # TODO: investigate and point to the docs, because this is weird.
    data = {
        "client_id": get_config(["env", "CLIENT_ID"]),
        "client_secret": get_config(["env", "CLIENT_SECRET"]),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{get_service_uri()}/continue-linking-session"
    }
    response = requests.post(
        get_config(["orcid", "tokenExchangeURL"]), headers=header, data=data
    )
    orcid_auth = json.loads(response.text)

    #
    # Now we store the response from ORCID in our session.
    # We still need the user to finalize the linking, now that it has succeeded
    # which is done in finalize-linking-session.
    #

    # Note that this is approximate, as it uses our time, not the
    # ORCID server time.
    session_record['orcid_auth'] = orcid_auth
    model = StorageModel()
    model.update_linking_session(session_id, session_record)

    #
    # Redirect back to the orcidlink interface, with some
    # options that support integration into workflows.
    #
    params = {}

    if "return_link" in session_record and session_record["return_link"] is not None:
        params["return_link"] = session_record["return_link"]

    if "skip_prompt" in session_record and session_record["skip_prompt"] is not None:
        params["skip_prompt"] = session_record["skip_prompt"]

    return responses.RedirectResponse(
        f"{get_config(['kbase', 'uiOrigin'])}?{urlencode(params)}#orcidlink/continue/{session_id}",
        status_code=302,
    )


@router.get("/linking-sessions/{session_id}", response_model=LinkingSessionComplete)
async def get_linking_sessions(
        session_id, authorization: str | None = Header(default=None)
):
    if authorization is None:
        raise HTTPException(401, 'Authorization required')

    session_record = get_linking_session_record(session_id, authorization)

    return {
        'session_id': session_id,
        'created_at': session_record['created_at'],
        'expires_at': session_record['expires_at'],
        'orcid_auth': {
            'scope': session_record['orcid_auth']['scope'],
            'name': session_record['orcid_auth']['name'],
            'orcid': session_record['orcid_auth']['orcid'],
            'expires_in': session_record['orcid_auth']['expires_in']
        }
    }


@router.post("/finish-linking-session", response_model=SimpleSuccess, responses={
    401: {
        "description": "Authorization not provided in header"
    }
})
async def finish_linking_session(
        session_info: SessionInfo,
        authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401, 'Authorization required')

    model = StorageModel()

    session_record = get_linking_session_record(session_info.session_id, authorization)

    username = get_username(authorization)
    created_at = current_time_millis()
    expires_at = created_at + session_record["orcid_auth"]["expires_in"] * 1000
    model.create_user_record(
        username,
        {
            "orcid_auth": session_record["orcid_auth"],
            "created_at": created_at,
            "expires_at": expires_at
        },
    )

    model.delete_linking_session(session_info.session_id)
    return {"ok": True}


class CreateLinkingSessionResult(BaseModel):
    session_id: str = Field(...)


@router.post("/linking-sessions", response_model=CreateLinkingSessionResult, responses={
    401: {
        "description": "Authorization not provided in header"
    }
})
async def create_linking_session(
        authorization: str | None = Header(default=None)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="A linking session requires authorization")

    created_at = current_time_millis()
    # 10 minute expiration
    expires_at = created_at + LINKING_SESSION_TTL * 1000
    session_id = str(uuid.uuid4())
    linking_record = {
        "session_id": session_id,
        "kbase_auth_token": authorization,
        "created_at": created_at,
        "expires_at": expires_at
    }
    model = StorageModel()
    model.create_linking_session(session_id, linking_record)
    return {'session_id': session_id}


@router.delete("/linking-sessions/{session_id}", response_model=SimpleSuccess, responses={
    401: {
        "description": "Authorization not provided in header"
    }
})
async def delete_linking_session(session_id, authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(401, 'Authorization required')

    session_record = get_linking_session_record(session_id, authorization)

    model = StorageModel()
    model.delete_linking_session(session_record['session_id'])
    return {"ok": True}


#
# Not-RESTful, i.e. interactive, API
#

#
# The initial url for linking to an ORCID Account
#
@router.get("/start-linking-session", responses={
    302: {
        "description": "Redirect to ORCID if a valid linking session"
    },
    404: {
        "description": "Response when a linking session not found for the supplied session id"
    }
})
async def start_linking_session(
        session_id: str,
        return_link: str | None = None,
        skip_prompt: str | None = None
):
    model = StorageModel()
    session_record = model.get_linking_session(session_id)
    if session_record is None:
        raise HTTPException(404, "Linking session not found")

    if return_link is not None:
        session_record['return_link'] = return_link

    if skip_prompt is not None:
        session_record['skip_prompt'] = skip_prompt

    model.update_linking_session(session_id, session_record)

    # TODO: get from config

    scope = ORCID_SCOPES

    # The redirect uri is back to ourselves ... this completes the interaction with ORCID, after
    # which we redirect back to whichever url the front end wants to return to.
    # But how to determine the path back here if we are running as a dynamic service?
    # Eventually this will be a core service, but for now let us solve this interesting
    # problem.
    # I think we just need to assume we are running on the "most released"; I don't think
    # there is a way for a dynamic service to know where it is running...
    # service_wizard = ServiceWizard(get_config(["kbase", "services", "ServiceWizard", "url"]), None)
    # service_info, error = service_wizard.get_service_status('ORCIDLink', None)
    params = {
        "client_id": get_config(["env", "CLIENT_ID"]),
        "response_type": "code",
        "scope": scope,
        "redirect_uri": f"{get_service_uri()}/continue-linking-session",
        "prompt": "login",
        "state": json.dumps({"session_id": session_id}),
    }
    url = f"{get_config(['orcid', 'authorizeURL'])}?{urlencode(params)}"
    return responses.RedirectResponse(url, status_code=302)
