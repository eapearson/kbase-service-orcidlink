from orcidlink import process
from orcidlink.jsonrpc.errors import NotAuthorizedError, NotFoundError
from orcidlink.model import LinkRecordPublic, ORCIDAuthPublic


async def owner_link(username: str, owner_username: str) -> LinkRecordPublic:
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


# REMOVED these, for now. Don't know whey they were useful.

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
