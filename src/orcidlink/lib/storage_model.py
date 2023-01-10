from typing import Optional

from orcidlink.lib.db import FileStorage
from orcidlink.model_types import LinkRecord


class StorageModel:

    def __init__(self):
        self.db = FileStorage()

    ##
    # Operations on the user record.
    # The user record is the primary linking document, providing a linkage between
    # a username and an ORCID Id.
    #
    def get_user_record(self, username: str) -> Optional[LinkRecord]:
        record = self.db.get('users', username)
        if record is None:
            return None
        return LinkRecord.parse_obj(record)

    def save_user_record(self, username, record):
        self.db.save('users', username, record)

    def create_user_record(self, username, record):
        self.db.create('users', username, record)

    def remove_user_record(self, username):
        self.db.delete('users', username)

    ################################
    # OAuth state persistence
    ################################

    # Linking session
    # TODO: operate with the linking session record model, not raw dict.

    def create_linking_session(self, session_id, linking_record):
        return self.db.create('linking-sessions', session_id, linking_record)

    def delete_linking_session(self, session_id):
        return self.db.delete('linking-sessions', session_id)

    def get_linking_session(self, session_id):
        return self.db.get('linking-sessions', session_id)

    def update_linking_session(self, session_id, session_record):
        return self.db.update('linking-sessions', session_id, session_record)
