import uuid

from lib.db import FileStorage


class StorageModel:

    def __init__(self):
        self.db = FileStorage()

    ##
    # Operations on the user record.
    # The user record is the primary linking document, providing a linkage between
    # a username and an ORCID Id.
    #
    def get_user_record(self, username):
        return self.db.get('users', username)

    def save_user_record(self, username, record):
        self.db.save('users', username, record)

    def create_user_record(self, username, record):
        self.db.create('users', username, record)

    def remove_user_record(self, username):
        self.db.delete('users', username)

    ################################
    # OAuth state persistence
    ################################

    def create_state_record(self, record):
        state_token = str(uuid.uuid4())
        self.db.create('start-state', state_token, record)
        return state_token

    def remove_state_record(self, state_token):
        return self.db.delete('start-state', state_token)

    def get_state_record(self, state_token):
        return self.db.get('start-state', state_token)

    # Linking session

    def create_linking_session(self, session_id, linking_record):
        return self.db.create('linking-sessions', session_id, linking_record)

    def delete_linking_session(self, session_id):
        return self.db.delete('linking-sessions', session_id)

    def get_linking_session(self, session_id):
        return self.db.get('linking-sessions', session_id)

    def update_linking_session(self, session_id, session_record):
        return self.db.update('linking-sessions', session_id, session_record)
