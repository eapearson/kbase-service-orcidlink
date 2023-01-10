from fastapi import Header
from orcidlink.lib.responses import ErrorResponse

AUTHORIZATION_HEADER = Header(default=None, description="KBase auth token")

AUTH_RESPONSES = {
    401: {"description": "KBase auth token absent"},
    403: {"description": "KBase auth token invalid"},
}

STD_RESPONSES = {
    422: {"description": "Either input or output data does not comply with the API schema",
          "model": ErrorResponse}
}
