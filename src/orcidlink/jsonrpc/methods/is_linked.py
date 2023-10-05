from orcidlink import process
from orcidlink.jsonrpc.errors import NotAuthorizedError


async def is_linked_method(username: str, auth_username: str) -> bool:
    """
    Given an arbitrary KBase username, and an authorized KBase username,
    determine if the given username has an ORCID Link.

    This method is useful for interfaces which need a quick and easy
    answer to the question "Is this user linked?".

    This method is designed to be used for and by the user who may be linked,
    and therefore the given and authorized username must be the same.
    """
    if username != auth_username:
        raise NotAuthorizedError(
            "Not authorized to inquire about the link for another user"
        )

    link_record = await process.link_record_for_user(username)

    return link_record is not None
