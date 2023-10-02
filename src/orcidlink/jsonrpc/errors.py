from fastapi_jsonrpc import BaseError


class AuthorizationRequiredError(BaseError):
    CODE = 1010
    MESSAGE = "Authorization Required"


class NotAuthorizedError(BaseError):
    CODE = 1011
    MESSAGE = "Not Authorized"


class ContentTypeError(BaseError):
    CODE = 1041
    MESSAGE = "Received Incorrect Content Type"


class JSONDecodeError(BaseError):
    CODE = 1040
    MESSAGE = "Error Decoding Response"


class UpstreamError(BaseError):
    CODE = 1050
    MESSAGE = "Upstream Error"


class NotFoundError(BaseError):
    CODE = 1020
    MESSAGE = "Not Found"


class AlreadyLinkedError(BaseError):
    CODE = 1000
    MESSAGE = "User already linked"
