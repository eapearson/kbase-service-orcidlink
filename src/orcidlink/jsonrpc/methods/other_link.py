from orcidlink import process
from orcidlink.jsonrpc.errors import NotFoundError
from orcidlink.model import LinkRecordPublicNonOwner, ORCIDAuthPublicNonOwner


async def other_link(username: str) -> LinkRecordPublicNonOwner:
    link_record = await process.link_record_for_user(username)

    if link_record is None:
        raise NotFoundError()

    return LinkRecordPublicNonOwner(
        username=link_record.username,
        orcid_auth=ORCIDAuthPublicNonOwner(
            name=link_record.orcid_auth.name, orcid=link_record.orcid_auth.orcid
        ),
    )
