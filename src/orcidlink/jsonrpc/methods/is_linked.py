from orcidlink import process
from orcidlink.jsonrpc.errors import NotAuthorizedError


async def is_linked_method(username: str, auth_username: str) -> bool:
    if username != auth_username:
        raise NotAuthorizedError("Not authorized to query for link for another user")

    link_record = await process.link_record_for_user(username)

    return link_record is not None
