import json
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, responses
from lib.auth import get_username
from lib.config import get_config, get_service_uri
from lib.constants import LINKING_SESSION_TTL, ORCID_SCOPES
from lib.responses import ensure_authorization, success_response_no_data
from lib.storage_model import StorageModel
from lib.utils import current_time_millis
from pydantic import BaseModel, Field

from src.lib.ORCIDClient import AuthorizeParams
from src.lib.route_utils import AUTHORIZATION_HEADER, AUTH_RESPONSES
from src.model_types import LinkingSessionComplete, ORCIDAuthPublic, SimpleSuccess

router = APIRouter(
    prefix="/linking-sessions",
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
        username = get_username(authorization)
        if not session_record['username'] == username:
            raise HTTPException(403, 'Username does not match linking session')
        # if not session_record['kbase_auth_token'] == authorization:
        #     raise HTTPException(403, 'Authorization does not match linking session')

    return session_record


#
# The initial call to create a linking session.
#

class CreateLinkingSessionResult(BaseModel):
    session_id: str = Field(...)


@router.post(
    "",
    response_model=CreateLinkingSessionResult,
    responses={
        **AUTH_RESPONSES
    },
    tags=["link"])
async def create_linking_session(
        authorization: str | None = AUTHORIZATION_HEADER
):
    """
    Creates a new "linking session"; resulting in a linking session created in the database, and the id for it
    returned for usage in an interactive linking session.
    """
    authorization = ensure_authorization(authorization)

    username = get_username(authorization)

    created_at = current_time_millis()
    # Expiration of the linking session, currently hardwired in the constants file.
    expires_at = created_at + LINKING_SESSION_TTL * 1000
    session_id = str(uuid.uuid4())
    linking_record = {
        "session_id": session_id,
        # "kbase_auth_token": authorization,
        "username": username,
        "created_at": created_at,
        "expires_at": expires_at
    }
    model = StorageModel()
    model.create_linking_session(session_id, linking_record)
    return CreateLinkingSessionResult(session_id=session_id)


SESSION_ID_FIELD = Field(..., description="The linking session id")
RETURN_LINK_QUERY = Query(default=None,
                          description="A url to redirect to after the entire linking is complete; not to be confused with the ORCID OAuth flow's redirect_url")
SKIP_PROMPT_QUERY = Query(default=None,
                          description="Whether to prompt for confirmation of linking; setting")


#
# The initial url for linking to an ORCID Account
#
@router.get(
    "/{session_id}/start",
    responses={
        302: {
            "description": "Redirect to ORCID if a valid linking session"
        },
        404: {
            "description": "Response when a linking session not found for the supplied session id"
        }
    },
    tags=["link"]
)
async def start_linking_session(
        session_id: str = SESSION_ID_FIELD,
        return_link: str | None = RETURN_LINK_QUERY,
        skip_prompt: str | None = SKIP_PROMPT_QUERY
):
    """
    Starts a "linking session", an interactive OAuth flow the end result of which is an access_token stored at
    KBase for future use by the user.
    """

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
    params = AuthorizeParams(
        client_id=get_config(["env", "CLIENT_ID"]),
        response_type="code",
        scope=scope,
        redirect_uri=f"{get_service_uri()}/continue-linking-session",
        prompt="login",
        state=json.dumps({"session_id": session_id})
    )
    url = f"{get_config(['orcid', 'authorizeURL'])}?{urlencode(params.dict())}"
    return responses.RedirectResponse(url, status_code=302)


@router.post(
    "/{session_id}/finish",
    response_model=SimpleSuccess,
    responses={
        **AUTH_RESPONSES
    },
    tags=["link"]
)
async def finish_linking_session(
        session_id: str = SESSION_ID_FIELD,
        authorization: str | None = AUTHORIZATION_HEADER
):
    """
    The final stage of the interactive linking session; called when the user confirms the creation
    of the link, after OAuth flow has finished.
    """
    ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    username = get_username(authorization)
    created_at = current_time_millis()
    expires_at = created_at + session_record["orcid_auth"]["expires_in"] * 1000

    model = StorageModel()
    model.create_user_record(
        username,
        {
            "orcid_auth": session_record["orcid_auth"],
            "created_at": created_at,
            "expires_at": expires_at
        },
    )

    model.delete_linking_session(session_id)
    return SimpleSuccess(ok="true")


#
# Managing linking sessions
#


@router.get(
    "/{session_id}",
    response_model=LinkingSessionComplete,
    responses={
        **AUTH_RESPONSES
    },
    tags=["link"]
)
async def get_linking_sessions(
        session_id: str = SESSION_ID_FIELD,
        authorization: str | None = AUTHORIZATION_HEADER
):
    ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    return LinkingSessionComplete(
        session_id=session_id,
        created_at=session_record['created_at'],
        expires_at=session_record['expires_at'],
        orcid_auth=ORCIDAuthPublic(
            scope=session_record['orcid_auth']['scope'],
            name=session_record['orcid_auth']['name'],
            orcid=session_record['orcid_auth']['orcid'],
            expires_in=session_record['orcid_auth']['expires_in']
        )
    )


@router.delete(
    "/{session_id}",
    response_model=SimpleSuccess,
    responses={
        204: {"description": "Successfully deleted the session"},
        **AUTH_RESPONSES
    },
    tags=["link"])
async def delete_linking_session(
        session_id: str = SESSION_ID_FIELD,
        authorization: str | None = AUTHORIZATION_HEADER
):
    ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    model = StorageModel()
    model.delete_linking_session(session_record['session_id'])
    return success_response_no_data()
