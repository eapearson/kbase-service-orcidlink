"""

Provides all support for creating an ORCID link.

This module implements an OAUTH flow and related services required to create an
ORCID Link and to fit into various front end usage scenarios.

"""
import json
import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Path, Query, responses, status
from pydantic import Field
from starlette.responses import RedirectResponse, Response

from orcidlink.lib import errors, exceptions
from orcidlink.lib.auth import ensure_authorization
from orcidlink.lib.responses import (
    AUTH_RESPONSES,
    AUTHORIZATION_HEADER,
    STD_RESPONSES,
    ui_error_response,
)
from orcidlink.lib.service_clients.orcid_api import AuthorizeParams
from orcidlink.lib.service_clients.orcid_oauth import orcid_oauth
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import (
    LinkingSessionCompletePublic,
    LinkingSessionInitial,
    LinkingSessionStarted,
    LinkRecord,
    SimpleSuccess,
)
from orcidlink.process import (
    delete_completed_linking_session,
    get_linking_session_completed,
)
from orcidlink.runtime import config
from orcidlink.storage.storage_model import storage_model

router = APIRouter(prefix="/linking-sessions")


async def get_linking_session_initial(
    session_id: str, authorization: str
) -> LinkingSessionInitial:
    _, token_info = await ensure_authorization(authorization)

    username = token_info.user

    model = storage_model()

    session_record = await model.get_linking_session_initial(session_id)

    if session_record is None:
        raise exceptions.NotFoundError("Linking session not found")

    if not session_record.username == username:
        raise exceptions.UnauthorizedError("Username does not match linking session")

    return session_record


async def get_linking_session_started(
    session_id: str, authorization: str
) -> LinkingSessionStarted:
    _, token_info = await ensure_authorization(authorization)

    username = token_info.user

    model = storage_model()

    session_record = await model.get_linking_session_started(session_id)

    if session_record is None:
        raise exceptions.NotFoundError("Linking session not found")

    if not session_record.username == username:
        raise exceptions.UnauthorizedError("Username does not match linking session")

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

UI_OPTIONS_QUERY = Query(default="", description="Opaque string of ui options")

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


class CreateLinkingSessionResult(ServiceBaseModel):
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
async def create_linking_session(
    authorization: str | None = AUTHORIZATION_HEADER,
) -> CreateLinkingSessionResult:
    """
    Create Linking Session

    Creates a new "linking session"; resulting in a linking session created in the
    database, and the id for it returned for usage in an interactive linking session.
    """
    _, token_info = await ensure_authorization(authorization)

    username = token_info.user

    # Check if username is already linked.
    model = storage_model()
    link_record = await model.get_link_record(username)

    if link_record is not None:
        raise exceptions.AlreadyLinkedError("User already has a link")

    created_at = posix_time_millis()

    expires_at = created_at + config().linking_session_lifetime * 1000
    session_id = str(uuid.uuid4())
    linking_record = LinkingSessionInitial(
        session_id=session_id,
        username=username,
        created_at=created_at,
        expires_at=expires_at,
    )

    await model.create_linking_session(linking_record)
    return CreateLinkingSessionResult(session_id=session_id)


@router.get(
    "/{session_id}",
    responses={
        200: {
            "description": "Returns the linking session",
            "model": LinkingSessionCompletePublic,
        },
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        404: {
            "description": "Linking session not found",
            "model": errors.ErrorResponse,
        },
        403: {
            "description": "User does not own linking session",
            "model": errors.ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def get_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT, authorization: str = AUTHORIZATION_HEADER
) -> LinkingSessionCompletePublic:
    """
    Get Linking Session

    Returns the linking session record identified by the given linking session id,
    as long as it is owned by the user associated with the given KBase auth token.

    Note that the
    """
    _, token_info = await ensure_authorization(authorization)

    # The only direct access to a linking session is when completed.
    linking_session = await get_linking_session_completed(session_id, token_info.user)

    #
    # Convert to public linking session to remove private info.
    #
    # NB 'kind' is configured as the discriminator for the types that compose
    # the LinkingSession union type. We could do this more simply, but
    # we need the conditional to satisfy mypy.
    # if linking_session.kind == "complete":
    return LinkingSessionCompletePublic.model_validate(linking_session.model_dump())

    # return linking_session


@router.delete(
    "/{session_id}",
    status_code=204,
    responses={
        204: {"description": "Successfully deleted the session"},
        **AUTH_RESPONSES,
        **STD_RESPONSES,
        403: {
            "description": "Username does not match linking session",
            "model": errors.ErrorResponse,
        },
        404: {
            "description": "Linking session not found",
            "model": errors.ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def delete_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> Response:
    """
    Delete Linking Session

    Deletes the linking session record associated with the session id provided
    in the url, as long as it is owned by the user associated with the provided
    KBase auth token.
    """
    _, token_info = await ensure_authorization(authorization)

    await delete_completed_linking_session(session_id, token_info.user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
            "model": errors.ErrorResponse,
        },
        404: {
            "description": "Linking session not found",
            "model": errors.ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def finish_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    authorization: str | None = AUTHORIZATION_HEADER,
) -> SimpleSuccess:
    """
    Finish Linking Session

    The final stage of the interactive linking session; called when the user confirms
    the creation of the link, after OAuth flow has finished.
    """
    authorization, token_info = await ensure_authorization(authorization)
    username = token_info.user

    session_record = await get_linking_session_completed(session_id, username)

    created_at = posix_time_millis()
    expires_at = created_at + session_record.orcid_auth.expires_in * 1000

    storage = storage_model()
    link_record = LinkRecord(
        username=username,
        orcid_auth=session_record.orcid_auth,
        created_at=created_at,
        expires_at=expires_at,
        retires_at=created_at + config().orcid_authorization_retirement_age * 1000,
    )
    await storage.create_link_record(link_record)

    await storage.delete_linking_session_completed(session_id)
    return SimpleSuccess(ok=True)


#
# OAuth Interactive Endpoints
#


#
# The initial url for linking to an ORCID Account
# Note that this is an interactive url - that is the browser is directly invoking this
# endpoint.
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
            "description": (
                "Response when a linking session not found for the supplied session id"
            ),
            "model": errors.ErrorResponse,
        },
    },
    tags=["linking-sessions"],
)
async def start_linking_session(
    session_id: str = SESSION_ID_PATH_ELEMENT,
    return_link: str | None = RETURN_LINK_QUERY,
    skip_prompt: bool = SKIP_PROMPT_QUERY,
    ui_options: str = UI_OPTIONS_QUERY,
    kbase_session: str = KBASE_SESSION_COOKIE,
    kbase_session_backup: str = KBASE_SESSION_BACKUP_COOKIE,
) -> RedirectResponse:
    # TODO: should be no json responses here!
    """
    Start Linking Session

    This endpoint is designed to be used directly by the browser. It is the "start"
    of the ORCID OAuth flow. If the provided session id is found and the associated
    session record is still in the initial state, it will initiate the OAuth flow
    by redirecting the browser to an endpoint at ORCID.

    Starts a "linking session", an interactive OAuth flow the end result of which is an
    access_token stored at KBase for future use by the user.
    """

    if kbase_session is None:
        if kbase_session_backup is None:
            raise exceptions.AuthorizationRequiredError(
                "Linking requires authentication"
            )
            # raise HTTPException(401, "Linking requires authentication")
        else:
            authorization = kbase_session_backup
    else:
        authorization = kbase_session

    await ensure_authorization(authorization)

    # We don't need the record, but we want to ensure it exists
    # and is owned by this user.
    await get_linking_session_initial(session_id, authorization)

    # TODO: enhance session record to record the status - so that we can prevent
    # starting a session twice!

    model = storage_model()
    await model.update_linking_session_to_started(
        session_id, return_link, skip_prompt, ui_options
    )

    # The redirect uri is back to ourselves ... this completes the interaction with
    # ORCID, after which we redirect back to whichever url the front end wants to
    # return to.
    # But how to determine the path back here if we are running as a dynamic service?
    # Eventually this will be a core service, but for now let us solve this interesting
    # problem.
    # I think we just need to assume we are running on the "most released"; I don't
    # think there is a way for a dynamic service to know where it is running...
    params = AuthorizeParams(
        client_id=config().orcid_client_id,
        response_type="code",
        scope=config().orcid_scopes,
        redirect_uri=f"{config().orcidlink_url}/linking-sessions/oauth/continue",
        prompt="login",
        state=json.dumps({"session_id": session_id}),
    )
    url = f"{config().orcid_oauth_base_url}/authorize?{urlencode(params.model_dump())}"
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
            "description": "Linking requires authorization; same meaning as standard "
            + "auth 401, but caught and issued in a different manner"
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
    # TODO: should be no json responses here@
    """
    Continue Linking Session

    This endpoint implements the handoff from from the ORCID authorization step in
    the ORCID OAuth flow. That is, it
    serves as the redirection target after the user has successfully completed
    their interaction with ORCID, at which they may have logged in and provided
    their consent to issuing the linking token to KBase.

    Note that this is an interstitional endpoint, which does not have its own
    user interface. Rather, it redirects to kbase-ui when finished. If an error is
    encountered, it redirects to an error viewing endpoint in kbase-ui.
    """
    # Note that this is the target for redirection from ORCID,
    # and we don't have an Authorization header. We don't
    # (necessarily) have an auth cookie.
    # So we use the state to get the session id.
    if kbase_session is None:
        if kbase_session_backup is None:
            # TODO: this should be our own exception, otherwise it will be caught by
            # the global fastapi hooks.
            raise exceptions.AuthorizationRequiredError(
                "Linking requires authentication"
            )
            # raise HTTPException(401, "Linking requires authentication")
        else:
            authorization = kbase_session_backup
    else:
        authorization = kbase_session

    authorization, _ = await ensure_authorization(authorization)

    #
    # TODO: MAJOR: ensure ui error responses are working; refactor
    #

    if error is not None:
        return ui_error_response(errors.ERRORS.linking_session_error, error)

    if code is None:
        return ui_error_response(
            errors.ERRORS.linking_session_continue_invalid_param,
            "The 'code' query param is required but missing",
        )

    if state is None:
        return ui_error_response(
            errors.ERRORS.linking_session_continue_invalid_param,
            "The 'state' query param is required but missing",
        )

    unpacked_state = json.loads(state)

    if "session_id" not in unpacked_state:
        return ui_error_response(
            errors.ERRORS.linking_session_continue_invalid_param,
            "The 'session_id' was not provided in the 'state' query param",
        )

    session_id = unpacked_state.get("session_id")
    session_record = await get_linking_session_started(session_id, authorization)

    #
    # Exchange the temporary token from ORCID for the authorized token.
    #
    orcid_auth = await orcid_oauth().exchange_code_for_token(code)

    #
    # Note that it isn't until this point that we know the orcid id the user
    # wants to link. So here we can detect if the orcid id has already
    # been linked. If so, it is an error.
    #
    model = storage_model()

    existing_orcid_auth = await model.get_link_record_for_orcid_id(orcid_auth.orcid)

    if existing_orcid_auth is not None:
        # Remove the session - it is not valid to use.
        await model.delete_linking_session_started(session_id)

        # TODO: send the orcid in case the user wants to investigate?
        return ui_error_response(
            errors.ERRORS.linking_session_already_linked_orcid,
            "The chosen ORCID account is already linked to another KBase account",
        )

    #
    # Now we store the response from ORCID in our session.
    # We still need the user to finalize the linking, now that it has succeeded
    # which is done in finalize-linking-session.
    #

    # Note that this is approximate, as it uses our time, not the
    # ORCID server time.

    await model.update_linking_session_to_finished(session_id, orcid_auth)

    #
    # Redirect back to the orcidlink interface, with some
    # options that support integration into workflows.
    #
    params = {}

    if session_record.return_link is not None:
        params["return_link"] = session_record.return_link

    params["skip_prompt"] = "true" if session_record.skip_prompt else "false"
    params["ui_options"] = session_record.ui_options

    return RedirectResponse(
        f"{config().ui_origin}?{urlencode(params)}#orcidlink/continue/{session_id}",
        status_code=302,
    )
