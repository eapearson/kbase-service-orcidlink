from orcidlink import process
from orcidlink.jsonrpc.errors import NotAuthorizedError, NotFoundError
from orcidlink.lib.service_clients.orcid_oauth import orcid_oauth
from orcidlink.model import (
    LinkRecordPublic,
    LinkRecordPublicNonOwner,
    ORCIDAuthPublic,
    ORCIDAuthPublicNonOwner,
)
from orcidlink.storage.storage_model import storage_model


async def link_method_for_owner(username: str, owner_username: str) -> LinkRecordPublic:
    link_record = await process.link_record_for_user(username)

    if link_record is None:
        raise NotFoundError()

    # This really shouldn't be raised normally; that would be a mis-use of this api.
    if link_record.username != owner_username:
        raise NotAuthorizedError("User not authorized to access this link")

    return LinkRecordPublic(
        username=link_record.username,
        created_at=link_record.created_at,
        expires_at=link_record.expires_at,
        retires_at=link_record.retires_at,
        orcid_auth=ORCIDAuthPublic(
            name=link_record.orcid_auth.name,
            scope=link_record.orcid_auth.scope,
            expires_in=link_record.orcid_auth.expires_in,
            orcid=link_record.orcid_auth.orcid,
        ),
    )


async def link_method_for_non_owner(username: str) -> LinkRecordPublicNonOwner:
    link_record = await process.link_record_for_user(username)

    if link_record is None:
        raise NotFoundError()

    return LinkRecordPublicNonOwner(
        username=link_record.username,
        orcid_auth=ORCIDAuthPublicNonOwner(
            name=link_record.orcid_auth.name, orcid=link_record.orcid_auth.orcid
        ),
    )


async def delete_link(username: str, owner_username: str) -> None:
    """
    Deletes the a linking record for a given user.
    """
    storage = storage_model()
    link_record = await storage.get_link_record(username)

    if link_record is None:
        raise NotFoundError("User does not have an ORCID Link")

    if link_record.username != owner_username:
        if link_record.username != owner_username:
            raise NotAuthorizedError("User not authorized to access this link")

    # TODO: handle error? or propagate? or in a transaction?
    await orcid_oauth().revoke_access_token(link_record.orcid_auth.access_token)

    # TODO: handle error? or propagate?
    await storage.delete_link_record(username)


# async def link_record_for_orcid_id(
#         orcid_id: str,
#         owner_username: str
# ) -> Optional[LinkRecord]:
#     #
#     # Fetch the user's ORCID Link record from KBase.
#     #
#     user_link_record = await storage_model().get_link_record_for_orcid_id(orcid_id)
#     if user_link_record is None:
#         return None
#         # raise exceptions.ServiceErrorY(
#         #     error=errors.ERRORS.not_found, message="ORCID Profile Not Found"
#         # )

#     if user_link_record.username != owner_username:
#         raise NotAuthorizedError("User not authorized to access this link")

#     # Make sure the orcid auth is not retired.
#     now = posix_time_millis()
#     if user_link_record.retires_at < now:
#         user_link_record = await process.refresh_token_for_link(user_link_record)

#     return user_link_record


# async def link_method_for_orcid(orcid_id: str, username: str) -> LinkRecordPublic:
#     link_record = await link_record_for_orcid_id(orcid_id, username)

#     if link_record is None:
#         raise NotFoundError()

#     return LinkRecordPublic(
#         username=link_record.username,
#         created_at=link_record.created_at,
#         expires_at=link_record.expires_at,
#         retires_at=link_record.retires_at,
#         orcid_auth=ORCIDAuthPublic(
#             name=link_record.orcid_auth.name,
#             scope=link_record.orcid_auth.scope,
#             expires_in=link_record.orcid_auth.expires_in,
#             orcid=link_record.orcid_auth.orcid,
#         ),
#     )
