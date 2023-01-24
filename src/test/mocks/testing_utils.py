def generate_kbase_token(part: str) -> str:
    return f"{part}{(32 - len(part)) * 'x'}"


TOKEN_FOO = generate_kbase_token("foo")
TOKEN_BAR = generate_kbase_token("bar")
TOKEN_BAZ = generate_kbase_token("baz")
