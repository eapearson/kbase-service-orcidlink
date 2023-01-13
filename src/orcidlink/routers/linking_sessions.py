import json
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Query, responses
from orcidlink.lib.config import config, get_service_url
from orcidlink.lib.constants import LINKING_SESSION_TTL, ORCID_SCOPES
from orcidlink.lib.responses import AUTHORIZATION_HEADER, AUTH_RESPONSES, STD_RESPONSES, ensure_authorization, \
    success_response_no_data
from orcidlink.lib.storage_model import storage_model
from orcidlink.lib.utils import current_time_millis
from orcidlink.model_types import LinkRecord, LinkingSessionComplete, LinkingSessionInitial, LinkingSessionStarted, \
    SimpleSuccess
from orcidlink.service_clients.ORCIDClient import AuthorizeParams
from orcidlink.service_clients.auth import get_username
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/linking-sessions",
    responses={404: {"description": "Not found"}}
)


##
# Convenience functions
#
def get_linking_session_record(session_id: str, authorization: str) -> LinkingSessionInitial | LinkingSessionStarted:
    username = get_username(authorization)

    model = storage_model()

    session_record = model.get_linking_session(session_id)

    if session_record is None:
        raise HTTPException(404, 'Linking session not found')

    if not session_record.username == username:
        raise HTTPException(403, 'Username does not match linking session')

    return session_record


#
# Commonly used fields
#
SESSION_ID_FIELD = Field(..., description="The linking session id")
RETURN_LINK_QUERY = Query(default=None,
                          description="A url to redirect to after the entire linking is complete; not to be confused with the ORCID OAuth flow's redirect_url")
SKIP_PROMPT_QUERY = Query(default=None,
                          description="Whether to prompt for confirmation of linking; setting")


#
# The initial call to create a linking session.
#

class CreateLinkingSessionResult(BaseModel):
    session_id: str = Field(...)


@router.post(
    "",
    response_model=CreateLinkingSessionResult,
    status_code=201,
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        201: {"description": "The linking session has been successfully created"}
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
    linking_record = LinkingSessionInitial(
        session_id=session_id,
        username=username,
        created_at=created_at,
        expires_at=expires_at
    )
    model = storage_model()
    model.create_linking_session(linking_record)
    return CreateLinkingSessionResult(session_id=session_id)


#
# The initial url for linking to an ORCID Account
# Note that this is an interactive url - that is the browser is directly invoking this endpoint.
# TODO: Errors should be redirects to the generic error handler in the ORCIDLink UI.
#
@router.get(
    "/{session_id}/start",
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
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
        skip_prompt: str = SKIP_PROMPT_QUERY,
        kbase_session: str = Cookie(default=None, description="KBase auth token taken from a cookie"),
        kbase_session_backup: str = Cookie(default=None, description="KBase auth token taken from a cookie"),

):
    """
    Starts a "linking session", an interactive OAuth flow the end result of which is an access_token stored at
    KBase for future use by the user.
    """

    if kbase_session is None:
        if kbase_session_backup is None:
            raise HTTPException(401, "Linking requires authentication")
        else:
            authorization = kbase_session_backup
    else:
        authorization = kbase_session

    username = get_username(authorization)

    model = storage_model()
    session_record = model.get_linking_session(session_id)

    if session_record is None:
        raise HTTPException(404, "Linking session not found")

    if session_record.username != username:
        raise HTTPException(403, "User not authorized to access this linking session")

    # Build updated session record
    # updated_session_record = LinkingSessionStarted(
    #     session_id=session_record.session_id,
    #     username=session_record.username,
    #     created_at=session_record.created_at,
    #     expires_at=session_record.expires_at,
    #     return_link=return_link,
    #     skip_prompt="no" if skip_prompt is None else skip_prompt
    # )

    # TODO: enhance session record to record the status - so that we can prevent
    # starting a session twice!

    model.update_linking_session_to_started(session_id, return_link, skip_prompt)

    # TODO: get from config; in fact, all constants probably should be!

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
        client_id=config().module.CLIENT_ID,
        response_type="code",
        scope=scope,
        redirect_uri=f"{get_service_url()}/continue-linking-session",
        prompt="login",
        state=json.dumps({"session_id": session_id})
    )
    url = f"{config().orcid.oauthBaseURL}/authorize?{urlencode(params.dict())}"
    return responses.RedirectResponse(url, status_code=302)


#
# Called when the linking session should be finalized, and saved to the database.
# The interactive design calls for an optional confirmation of the creation of the link
# after the oauth flow.
#
@router.put(
    "/{session_id}/finish",
    response_model=SimpleSuccess,
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {"description": "The linking session has been finished successfully"}
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
    expires_at = created_at + session_record.orcid_auth.expires_in * 1000

    model = storage_model()
    link_record = LinkRecord(
        username=username,
        orcid_auth=session_record.orcid_auth,
        created_at=created_at,
        expires_at=expires_at
    )
    model.create_link_record(link_record)

    model.delete_linking_session(session_id)
    return SimpleSuccess(ok="true")


#
# Managing linking sessions
#


@router.get(
    "/{session_id}",
    response_model=LinkingSessionComplete | LinkingSessionStarted | LinkingSessionInitial,
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        200: {"description": "Returns the current linking session, scrubbed of private info"}
    },
    tags=["link"]
)
async def get_linking_sessions(
        session_id: str = SESSION_ID_FIELD,
        authorization: str = AUTHORIZATION_HEADER
):
    ensure_authorization(authorization)

    return get_linking_session_record(session_id, authorization)

    # if 'orcid_auth' in session_record:
    #     return LinkingSessionComplete(
    #         session_id=session_id,
    #         username=session_record.username.,
    #         created_at=session_record['created_at'],
    #         expires_at=session_record['expires_at'],
    #         orcid_auth=ORCIDAuthPublic(
    #             scope=session_record['orcid_auth']['scope'],
    #             name=session_record['orcid_auth']['name'],
    #             orcid=session_record['orcid_auth']['orcid'],
    #             expires_in=session_record['orcid_auth']['expires_in']
    #         )
    #     )
    # elif 'skip_prompt' in session_record:
    #     linking_session_started = LinkingSessionStarted(
    #         session_id=session_id,
    #         username=session_record['username'],
    #         skip_prompt=session_record['skip_prompt'],
    #         created_at=session_record['created_at'],
    #         expires_at=session_record['expires_at']
    #     )
    #     if 'return_link' in session_record:
    #         linking_session_started.return_link = session_record['return_link']
    #     return linking_session_started
    # else:
    #     return LinkingSessionInitial(
    #         session_id=session_id,
    #         username=session_record['username'],
    #         created_at=session_record['created_at'],
    #         expires_at=session_record['expires_at']
    #     )


@router.delete(
    "/{session_id}",
    response_model=SimpleSuccess,
    responses={
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        204: {"description": "Successfully deleted the session"}
    },
    tags=["link"])
async def delete_linking_session(
        session_id: str = SESSION_ID_FIELD,
        authorization: str | None = AUTHORIZATION_HEADER
):
    ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    model = storage_model()
    model.delete_linking_session(session_record.session_id)
    return success_response_no_data()
