from orcidlink.storage.storage_model import storage_model


def generate_kbase_token(part: str) -> str:
    return f"{part}{(32 - len(part)) * 'x'}"


TOKEN_FOO = generate_kbase_token("foo")
TOKEN_BAR = generate_kbase_token("bar")
TOKEN_BAZ = generate_kbase_token("baz")


def clear_storage_model():
    sm = storage_model()
    sm.db.linking_sessions_completed.delete_many({})
    sm.db.linking_sessions_initial.delete_many({})
    sm.db.linking_sessions_started.delete_many({})
    sm.db.links.delete_many({})
