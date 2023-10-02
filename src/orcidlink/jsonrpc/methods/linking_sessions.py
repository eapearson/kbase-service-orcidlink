import uuid

from orcidlink.jsonrpc.errors import AlreadyLinkedError, NotAuthorizedError
from orcidlink.jsonrpc.methods.common import (
    SESSION_ID_FIELD,
    get_linking_session_completed,
)
from orcidlink.lib.service_clients.orcid_oauth import orcid_oauth
from orcidlink.lib.type import ServiceBaseModel
from orcidlink.lib.utils import posix_time_millis
from orcidlink.model import (
    LinkingSessionCompletePublic,
    LinkingSessionInitial,
    LinkRecord,
)
from orcidlink.runtime import config
from orcidlink.storage.storage_model import storage_model


class CreateLinkingSessionResult(ServiceBaseModel):
    session_id: str = SESSION_ID_FIELD


async def create_linking_session(
    username: str, auth_username: str
) -> CreateLinkingSessionResult:
    # May seeem silly, but we can only create a link for ourself.

    if username != auth_username:
        raise NotAuthorizedError("Only the account owner may create a link")

    model = storage_model()
    link_record = await model.get_link_record(username)

    if link_record is not None:
        raise AlreadyLinkedError("User already has a link")

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


async def get_linking_session(
    session_id: str, auth_username: str
) -> LinkingSessionCompletePublic:
    model = storage_model()
    session_record = await get_linking_session_completed(
        model, session_id, auth_username
    )

    #
    # Convert to public linking session to remove private info.
    #
    return LinkingSessionCompletePublic.model_validate(session_record.model_dump())


async def delete_linking_session(session_id: str, auth_username: str) -> None:
    storage = storage_model()
    session_record = await get_linking_session_completed(
        storage, session_id, auth_username
    )

    await storage.delete_linking_session_completed(session_record.session_id)

    # TODO: handle error? or propagate? or in a transaction?
    await orcid_oauth().revoke_access_token(session_record.orcid_auth.access_token)

    return None


async def finish_linking_session(session_id: str, auth_username: str) -> None:
    """
    Finish Linking Session

    The final stage of the interactive linking session; called when the user confirms
    the creation of the link, after OAuth flow has finished. Its job is to delete
    the completed linking session record, and to create the link itself.
    """
    storage = storage_model()
    session_record = await get_linking_session_completed(
        storage, session_id, auth_username
    )

    created_at = posix_time_millis()
    expires_at = created_at + session_record.orcid_auth.expires_in * 1000

    storage = storage_model()
    link_record = LinkRecord(
        username=session_record.username,
        orcid_auth=session_record.orcid_auth,
        created_at=created_at,
        expires_at=expires_at,
        retires_at=created_at + config().orcid_authorization_retirement_age * 1000,
    )
    await storage.create_link_record(link_record)

    await storage.delete_linking_session_completed(session_id)

    return None
