import json
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Path, Query, responses
from orcidlink.lib.config import config
from orcidlink.lib.constants import LINKING_SESSION_TTL, ORCID_SCOPES
from orcidlink.lib.responses import (
    AUTHORIZATION_HEADER,
    AUTH_RESPONSES,
    ErrorResponse,
    STD_RESPONSES,
    ensure_authorization,
    error_response,
    success_response_no_data,
    ui_error_response,
)
from orcidlink.lib.utils import current_time_millis
from orcidlink.model import (
    LinkRecord,
    LinkingSessionComplete,
    LinkingSessionInitial,
    LinkingSessionStarted,
    SimpleSuccess,
)
from orcidlink.service_clients.ORCIDClient import AuthorizeParams, orcid_oauth
from orcidlink.service_clients.auth import get_username
from orcidlink.storage.storage_model import storage_model
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse

router = APIRouter(prefix="/linking-sessions")


##
# Convenience functions
#
def get_linking_session_record(
    session_id: str, authorization: str
) -> LinkingSessionInitial | LinkingSessionStarted | LinkingSessionComplete:
    _, token_info = ensure_authorization(authorization)

    username = token_info.user

    model = storage_model()

    session_record = model.get_linking_session(session_id)

    if session_record is None:
        raise HTTPException(404, "Linking session not found")

    if not session_record.username == username:
        raise HTTPException(403, "Username does not match linking session")

    return session_record


#
# Commonly used fields
#
SESSION_ID_FIELD = Field(
    description="The linking session id",
    # It is a uuid, whose string representation is 36 characters.
    min_length=36,
    max_length=36,
)
SESSION_ID_PATH_ELEMENT = Path(
    description="The linking session id",
    # It is a uuid, whose string representation is 36 characters.
    min_length=36,
    max_length=36,
)
RETURN_LINK_QUERY = Query(
    default=None,
    description="A url to redirect to after the entire linking is complete; "
    + "not to be confused with the ORCID OAuth flow's redirect_url",
)
SKIP_PROMPT_QUERY = Query(
    default=None, description="Whether to prompt for confirmation of linking"
)

KBASE_SESSION_COOKIE = Cookie(
    default=None,
    description="KBase auth token taken from a cookie named 'kbase_session'",
)

KBASE_SESSION_BACKUP_COOKIE = Cookie(
    default=None,
    description="KBase auth token taken from a cookie named 'kbase_session_backup. "
    + "Required in the KBase production environment since the prod ui and services "
    + "operate on different hosts; the primary cookie, kbase_session, is host-based "
    "so cannot be read by a prod service.",
)


#
# The initial call to create a linking session.
#


class CreateLinkingSessionResult(BaseModel):
    session_id: str = SESSION_ID_FIELD


# TODO: error if link already exists for this user.
@router.post(
    "",
    response_model=CreateLinkingSessionResult,
    status_code=201,
    responses={
        201: {"description": "The linking session has been successfully created"},
        **AUTH_RESPONSES,
        **STD_RESPONSES,
    },
    tags=["linking-sessions"],
)
async def create_linking_session(authorization: str | None = AUTHORIZATION_HEADER):
    """
    Create Linking Session

    Creates a new "linking session"; resulting in a linking session created in the database, and the id for it
    returned for usage in an interactive linking session.
    """
    _, token_info = ensure_authorization(authorization)

    username = token_info.user

    created_at = current_time_millis()
    # Expiration of the linking session, currently hardwired in the constants file.
    expires_at = created_at + LINKING_SESSION_TTL * 1000
    session_id = str(uuid.uuid4())
    linking_record = LinkingSessionInitial(
        session_id=session_id,
        username=username,
        created_at=created_at,
        expires_at=expires_at,
    )
    model = storage_model()
    model.create_linking_session(linking_record)
    return CreateLinkingSessionResult(session_id=session_id)


@router.get(
    "/{session_id}",
    responses={
        200: {
            "description": "Returns the linking session",
            "model": LinkingSessionStarted | LinkingSessionInitial,
        },
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {"description": "Linking session not found", "model": ErrorResponse},
        403: {
            "description": "User does not own linking session",
            "model": ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def get_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT, authorization: str = AUTHORIZATION_HEADER
):
    """
    Get Linking Session

    Returns the linking session record identified by the given linking session id,
    as long as it is owned by the user associated with the given KBase auth token.
    """
    _, token_info = ensure_authorization(authorization)

    linking_session = get_linking_session_record(session_id, authorization)
    if type(linking_session) == LinkingSessionComplete:
        return error_response(
            "session-complete",
            "Linking Session Completed",
            "Attempt to return a completed linking session rejected",
        )
    return linking_session


@router.delete(
    "/{session_id}",
    status_code=204,
    responses={
        204: {"description": "Successfully deleted the session"},
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        403: {
            "description": "Username does not match linking session",
            "model": ErrorResponse,
        },
        404: {"description": "Linking session not found", "model": ErrorResponse},
    },
    tags=["linking-sessions"],
)
async def delete_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    authorization: str | None = AUTHORIZATION_HEADER,
):
    """
    Delete Linking Session

    Deletes the linking session record associated with the session id provided
    in the url, as long as it is owned by the user associated with the provided
    KBase auth token.
    """
    authorization, _ = ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    model = storage_model()
    model.delete_linking_session(session_record.session_id)
    return success_response_no_data()


#
# Called when the linking session should be finalized, and saved to the database.
# The interactive design calls for an optional confirmation of the creation of the link
# after the oauth flow.
#
@router.put(
    "/{session_id}/finish",
    response_model=SimpleSuccess,
    responses={
        200: {
            "description": "The linking session has been finished successfully",
            "model": SimpleSuccess,
        },
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        403: {
            "description": "Username does not match linking session",
            "model": ErrorResponse,
        },
        404: {"description": "Linking session not found", "model": ErrorResponse},
    },
    tags=["linking-sessions"],
)
async def finish_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    authorization: str | None = AUTHORIZATION_HEADER,
):
    """
    Finish Linking Session

    The final stage of the interactive linking session; called when the user confirms the creation
    of the link, after OAuth flow has finished.
    """
    authorization, _ = ensure_authorization(authorization)

    session_record = get_linking_session_record(session_id, authorization)

    if not type(session_record) == LinkingSessionComplete:
        return error_response(
            "invalidState",
            "Invalid Linking Session State",
            "The linking session must be in 'complete' state, but is not",
            status_code=400,
        )

    username = get_username(authorization)
    created_at = current_time_millis()
    expires_at = created_at + session_record.orcid_auth.expires_in * 1000

    model = storage_model()
    link_record = LinkRecord(
        username=username,
        orcid_auth=session_record.orcid_auth,
        created_at=created_at,
        expires_at=expires_at,
    )
    model.create_link_record(link_record)

    model.delete_linking_session(session_id)
    return SimpleSuccess(ok="true")


#
# OAuth Interactive Endpoints
#

#
# The initial url for linking to an ORCID Account
# Note that this is an interactive url - that is the browser is directly invoking this endpoint.
# TODO: Errors should be redirects to the generic error handler in the ORCIDLink UI.
#
@router.get(
    "/{session_id}/oauth/start",
    response_class=RedirectResponse,
    status_code=302,
    responses={
        302: {"description": "Redirect to ORCID if a valid linking session"},
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {
            "description": "Response when a linking session not found for the supplied session id",
            "model": ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def start_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    return_link: str | None = RETURN_LINK_QUERY,
    skip_prompt: str = SKIP_PROMPT_QUERY,
    kbase_session: str = KBASE_SESSION_COOKIE,
    kbase_session_backup: str = KBASE_SESSION_BACKUP_COOKIE,
):
    """
    Start Linking Session

    This endpoint is designed to be used directly by the browser. It is the "start"
    of the ORCID OAuth flow. If the provided session id is found and the associated
    session record is still in the initial state, it will initiate the OAuth flow
    by redirecting the browser to an endpoint at ORCID.

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

    _, token_info = ensure_authorization(authorization)

    username = token_info.user

    model = storage_model()
    session_record = model.get_linking_session(session_id)

    if session_record is None:
        raise HTTPException(404, "Linking session not found")

    if session_record.username != username:
        raise HTTPException(403, "User not authorized to access this linking session")

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
    params = AuthorizeParams(
        client_id=config().orcid.clientId,
        response_type="code",
        scope=scope,
        redirect_uri=f"{config().services.ORCIDLink.url}/linking-sessions/oauth/continue",
        prompt="login",
        state=json.dumps({"session_id": session_id}),
    )
    url = f"{config().orcid.oauthBaseURL}/authorize?{urlencode(params.dict())}"
    return responses.RedirectResponse(url, status_code=302)


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
@router.get(
    "/oauth/continue",
    status_code=302,
    response_class=RedirectResponse,
    responses={
        302: {
            "description": "Redirect to the continuation page; or error page",
        },
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        401: {
            "description": "Linking requires authorization; same meaning as standard auth 401, "
            + "but caught and issued in a different manner"
        },
    },
    tags=["linking-sessions"],
)
async def linking_sessions_continue(
    kbase_session: str = KBASE_SESSION_COOKIE,
    kbase_session_backup: str = KBASE_SESSION_BACKUP_COOKIE,
    code: str
    | None = Query(
        default=None,
        description="For a success case, contains an OAuth exchange code parameter",
    ),
    state: str
    | None = Query(
        default=None,
        description="For a success case, contains an OAuth state parameter",
    ),
    error: str
    | None = Query(
        default=None, description="For an error case, contains an error code parameter"
    ),
) -> RedirectResponse:
    """
    Continue Linking Session

    This endpoint implements the end point for the ORCID OAuth flow. That is, it
    serves as the redirection target after the user has successfully completed
    their interaction with ORCID, at which they may have logged in and provided
    their consent to issuing the linking token to KBase.

    Note that since this is an "interactive" endpoint, which does not have its own
    user interface, rather redirects to kbase-ui when finished. This applies to
    errors as well. Errors are displayed by redirecting the browser to an endpoint
    in kbase-ui which is designed to expect the error values for display to be
    in the url itself.
    """
    # Note that this is the target for redirection from ORCID,
    # and we don't have an Authorization header. We don't
    # (necessarily) have an auth cookie.
    # So we use the state to get the session id.
    if kbase_session is None:
        if kbase_session_backup is None:
            # TODO: this should be our own exception, otherwise it will be caught by
            # the global fastapi hooks.
            raise HTTPException(401, "Linking requires authentication")
        else:
            authorization = kbase_session_backup
    else:
        authorization = kbase_session

    authorization, _ = ensure_authorization(authorization)

    if error is not None:
        return ui_error_response("link.orcid_error", "ORCID Error Linking", error)

    if code is None:
        return ui_error_response(
            "link.code_missing",
            "Linking code missing",
            "The 'code' query param is required but missing",
        )

    if state is None:
        return ui_error_response(
            "link.state_missing",
            "Linking state missing",
            "The 'state' query param is required but missing",
        )

    unpacked_state = json.loads(state)

    if "session_id" not in unpacked_state:
        return ui_error_response(
            "link.session_id_missing",
            "Linking Error",
            "The 'session_id' was not provided in the 'state' query param",
        )

    session_id = unpacked_state.get("session_id")

    session_record = get_linking_session_record(session_id, authorization)

    if not type(session_record) == LinkingSessionStarted:
        return ui_error_response(
            "linking_session.wrong_state",
            "Linking Error",
            "The session is not in 'started' state",
        )

    #
    # Exchange the temporary token from ORCID for the authorized token.
    #
    # def exchange_code_for_token(self, code: str):
    orcid_auth = orcid_oauth(authorization).exchange_code_for_token(code)

    # header = {
    #     "accept": "application/json",
    #     "content-type": "application/x-www-form-urlencoded",
    # }
    # # Note that the redirect uri below is just for the api - it is not actually used
    # # for redirection in this case.
    # # TODO: investigate and point to the docs, because this is weird.
    # # TODO: put in orcid client!
    # data = {
    #     "client_id": config().orcid.clientId,
    #     "client_secret": config().orcid.clientSecret,
    #     "grant_type": "authorization_code",
    #     "code": code,
    #     "redirect_uri": f"{config().services.ORCIDLink.url}/linking-sessions/oauth/continue",
    # }
    # response = httpx.post(
    #     f"{config().orcid.oauthBaseURL}/token", headers=header, data=data
    # )
    # orcid_auth = ORCIDAuth.parse_obj(json.loads(response.text))

    #
    # Now we store the response from ORCID in our session.
    # We still need the user to finalize the linking, now that it has succeeded
    # which is done in finalize-linking-session.
    #

    # Note that this is approximate, as it uses our time, not the
    # ORCID server time.
    # session_record.orcid_auth = orcid_auth
    model = storage_model()
    model.update_linking_session_to_finished(session_id, orcid_auth)

    #
    # Redirect back to the orcidlink interface, with some
    # options that support integration into workflows.
    #
    params = {}

    if session_record.return_link is not None:
        params["return_link"] = session_record.return_link

    params["skip_prompt"] = session_record.skip_prompt

    return RedirectResponse(
        f"{config().ui.origin}?{urlencode(params)}#orcidlink/continue/{session_id}",
        status_code=302,
    )


#
# Managing linking sessions
#
