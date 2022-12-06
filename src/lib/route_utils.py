from fastapi import Header

AUTHORIZATION_HEADER = Header(default=None, description="KBase auth token")

AUTH_RESPONSES = {
    401: {"description": "KBase auth token absent"},
    403: {"description": "KBase auth token invalid"},
}
