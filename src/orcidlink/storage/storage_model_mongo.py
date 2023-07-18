from typing import Any, Dict, Optional

from pymongo import MongoClient

from orcidlink.lib import errors
from orcidlink.model import (
    LinkingSessionComplete,
    LinkingSessionInitial,
    LinkingSessionStarted,
    LinkRecord,
    ORCIDAuth,
)


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
            retrywrites=False,
        )
        self.db = self.client[database]

    ##
    # Operations on the user record.
    # The user record is the primary linking document, providing a linkage between
    # a username and an ORCID Id.
    #
    def get_link_record(self, username: str) -> Optional[LinkRecord]:
        record = self.db.links.find_one({"username": username})

        if record is None:
            return None

        parsed = LinkRecord.model_validate(record)

        return parsed

    def save_link_record(self, record: LinkRecord) -> None:
        self.db.links.update_one(
            {"username": record.username}, {"$set": record.model_dump()}
        )

    def create_link_record(self, record: LinkRecord) -> None:
        self.db.links.insert_one(record.model_dump())

    def delete_link_record(self, username: str) -> None:
        self.db.links.delete_one({"username": username})

    ################################
    # OAuth state persistence
    ################################

    # Linking session
    # TODO: operate with the linking session record model, not raw dict.

    def create_linking_session(self, linking_record: LinkingSessionInitial) -> None:
        self.db.linking_sessions_initial.insert_one(linking_record.model_dump())
        # return self.db.create('linking-sessions', session_id, linking_record)

    def delete_linking_session(self, session_id: str) -> None:
        # The UI api only supports deleting completed sessions.
        # We'll need an admin API to delete danging initial and started linking sessions.
        self.db.linking_sessions_completed.delete_one({"session_id": session_id})

    # def get_linking_session(
    #     self, session_id: str
    # ) -> LinkingSessionInitial | LinkingSessionStarted | LinkingSessionComplete | None:
    #     session = self.db.linking_sessions.find_one({"session_id": session_id})

    #     if session is None:
    #         return None
    #     if "orcid_auth" in session:
    #         session["kind"] = "complete"
    #         return LinkingSessionComplete.model_validate(session)
    #     elif "skip_prompt" in session:
    #         session["kind"] = "started"
    #         return LinkingSessionStarted.model_validate(session)
    #     else:
    #         session["kind"] = "initial"
    #         return LinkingSessionInitial.model_validate(session)

    def get_linking_session_initial(
        self, session_id: str
    ) -> LinkingSessionInitial | None:
        session = self.db.linking_sessions_initial.find_one({"session_id": session_id})

        if session is None:
            return None
        else:
            # session["kind"] = "initial"
            return LinkingSessionInitial.model_validate(session)

    def get_linking_session_started(
        self, session_id: str
    ) -> LinkingSessionStarted | None:
        session = self.db.linking_sessions_started.find_one({"session_id": session_id})
        if session is None:
            return None
        else:
            return LinkingSessionStarted.model_validate(session)

    def get_linking_session_completed(
        self, session_id: str
    ) -> LinkingSessionComplete | None:
        session = self.db.linking_sessions_completed.find_one(
            {"session_id": session_id}
        )

        if session is None:
            return None
        else:
            # session["kind"] = "complete"
            return LinkingSessionComplete.model_validate(session)

    def update_linking_session_to_started(
        self,
        session_id: str,
        return_link: str | None,
        skip_prompt: bool,
        ui_options: str,
    ) -> None:
        with self.client.start_session() as session:
            # Get the initial linking session.
            linking_session = self.db.linking_sessions_initial.find_one(
                {"session_id": session_id}, session=session
            )

            if linking_session is None:
                raise errors.NotFoundError("Linking session not found")

            linking_session["return_link"] = return_link
            linking_session["skip_prompt"] = skip_prompt
            linking_session["ui_options"] = ui_options

            self.db.linking_sessions_started.insert_one(
                linking_session, session=session
            )

            self.db.linking_sessions_initial.delete_one(
                {"session_id": session_id}, session=session
            )

    def update_linking_session_to_finished(
        self, session_id: str, orcid_auth: ORCIDAuth
    ) -> None:
        with self.client.start_session() as session:
            # Get the initial linking session.
            linking_session = self.db.linking_sessions_started.find_one(
                {"session_id": session_id}, session=session
            )

            if linking_session is None:
                raise errors.NotFoundError("Linking session not found")

            linking_session["orcid_auth"] = orcid_auth.model_dump()

            self.db.linking_sessions_completed.insert_one(
                linking_session, session=session
            )

            self.db.linking_sessions_started.delete_one(
                {"session_id": session_id}, session=session
            )

    def reset_database(self) -> None:
        self.db.links.drop()
        self.db.linking_sessions_initial.drop()
        self.db.linking_sessions_started.drop()
        self.db.linking_sessions_completed.drop()
        self.db.description.drop()
