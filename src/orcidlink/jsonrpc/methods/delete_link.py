from orcidlink.jsonrpc.errors import NotAuthorizedError, NotFoundError
from orcidlink.lib.service_clients.kbase_auth import AccountInfo
from orcidlink.lib.service_clients.orcid_oauth_api import orcid_oauth_api
from orcidlink.runtime import config
from orcidlink.storage.storage_model import storage_model


async def delete_link(username: str, account_info: AccountInfo) -> None:
    """
    Deletes the a linking record for a given user; to be called only by
    a manager.
    """
    if config().manager_role not in account_info.customroles:
        raise NotAuthorizedError("Not authorized for management operations")

    storage = storage_model()
    link_record = await storage.get_link_record(username)

    if link_record is None:
        raise NotFoundError("User does not have an ORCID Link")

    # TODO: handle error? or propagate? or in a transaction?
    await orcid_oauth_api().revoke_access_token(link_record.orcid_auth.access_token)

    # TODO: handle error? or propagate?
    await storage.delete_link_record(username)
