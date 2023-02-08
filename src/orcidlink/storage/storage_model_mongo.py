from typing import Any, Dict, Optional

from orcidlink.model import (
    LinkRecord,
    LinkingSessionComplete,
    LinkingSessionInitial,
    LinkingSessionStarted,
    ORCIDAuth,
)
from pymongo import MongoClient


class StorageModelMongo:
    def __init__(
            self, host: str, port: int, database: str, username: str, password: str
    ):
        self.client: MongoClient[Dict[str, Any]] = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=database,
            retrywrites=False
        )
        self.db = self.client[database]

    ##
    # Operations on the user record.
    # The user record is the primary linking document, providing a linkage between
    # a username and an ORCID Id.
    #
    def get_link_record(self, username: str) -> Optional[LinkRecord]:
        record = self.db.links.find_one({"username": username})

        # record = self.db.get('users', username)
        if record is None:
            return None
        return LinkRecord.parse_obj(record)

    def save_link_record(self, record: LinkRecord) -> None:
        self.db.links.update_one({"username": record.username}, {"$set": record.dict()})

    def create_link_record(self, record: LinkRecord) -> None:
        self.db.links.insert_one(record.dict())

    def delete_link_record(self, username: str) -> None:
        self.db.links.delete_one({"username": username})

    ################################
    # OAuth state persistence
    ################################

    # Linking session
    # TODO: operate with the linking session record model, not raw dict.

    def create_linking_session(self, linking_record: LinkingSessionInitial) -> None:
        self.db.linking_sessions.insert_one(linking_record.dict())
        # return self.db.create('linking-sessions', session_id, linking_record)

    def delete_linking_session(self, session_id: str) -> None:
        self.db.linking_sessions.delete_one({"session_id": session_id})

    def get_linking_session(
            self, session_id: str
    ) -> LinkingSessionInitial | LinkingSessionStarted | LinkingSessionComplete | None:
        session = self.db.linking_sessions.find_one({"session_id": session_id})
        if session is None:
            return None
        if "orcid_auth" in session:
            return LinkingSessionComplete.parse_obj(session)
        elif "skip_prompt" in session:
            return LinkingSessionStarted.parse_obj(session)
        else:
            return LinkingSessionInitial.parse_obj(session)

    def update_linking_session_to_started(
            self, session_id: str, return_link: str | None, skip_prompt: str
    ) -> None:
        update = {"return_link": return_link, "skip_prompt": skip_prompt}
        self.db.linking_sessions.update_one(
            {"session_id": session_id}, {"$set": update}
        )

    def update_linking_session_to_finished(
            self, session_id: str, orcid_auth: ORCIDAuth
    ) -> None:
        update = {"orcid_auth": orcid_auth.dict()}
        self.db.linking_sessions.update_one(
            {"session_id": session_id}, {"$set": update}
        )

    def reset_database(self) -> None:
        self.db.links.drop()
        self.db.linking_sessions.drop()
