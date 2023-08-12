from orcidlink.storage.storage_model import storage_model


def generate_kbase_token(part: str) -> str:
    return f"{part}{(32 - len(part)) * 'x'}"


TOKEN_FOO = generate_kbase_token("foo")
TOKEN_BAR = generate_kbase_token("bar")
TOKEN_BAZ = generate_kbase_token("baz")


async def clear_storage_model():
    sm = storage_model()
    await sm.db.linking_sessions_completed.delete_many({})
    await sm.db.linking_sessions_initial.delete_many({})
    await sm.db.linking_sessions_started.delete_many({})
    await sm.db.links.delete_many({})
