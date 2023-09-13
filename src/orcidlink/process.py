from orcidlink.lib import exceptions
from orcidlink.lib.service_clients.orcid_api import orcid_oauth
from orcidlink.model import LinkingSessionComplete
from orcidlink.storage.storage_model import storage_model


async def delete_link(username: str) -> None:
    storage = storage_model()
    link_record = await storage.get_link_record(username)

    if link_record is None:
        raise exceptions.NotFoundError("User does not have an ORCID Link")

    # TODO: handle error? or propagate? or in a transaction?
    await orcid_oauth(link_record.orcid_auth.access_token).revoke_token()

    # TODO: handle error? or propagate?
    await storage.delete_link_record(username)


async def get_linking_session_completed(
    session_id: str, username: str
) -> LinkingSessionComplete:
    model = storage_model()

    session_record = await model.get_linking_session_completed(session_id)

    if session_record is None:
        raise exceptions.NotFoundError("Linking session not found")

    if session_record.username != username:
        raise exceptions.UnauthorizedError("Username does not match linking session")

    return session_record


async def delete_completed_linking_session(session_id: str, username: str) -> None:
    storage = storage_model()

    session_record = await get_linking_session_completed(session_id, username)

    storage = storage_model()
    await storage.delete_linking_session_completed(session_record.session_id)

    # TODO: handle error? or propagate? or in a transaction?
    await orcid_oauth(session_record.orcid_auth.access_token).revoke_token()
