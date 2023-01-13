class ServiceError(Exception):
    """
    A general purpose exception mechanism mirroring the
    """

    def __init__(self, code: int = None, name: str = None, message: str = None, data: str = None):
        super().__init__(message)
        if code is None:
            raise ValueError('The "code" named argument is required')
        self.code = code

        if name is None:
            raise ValueError('The "name" named argument is required')
        self.name = name

        if message is None:
            raise ValueError('The "message" named argument is required')
        self.message = message

        # Data is optional.
        self.data = data


# Standard JSON-RPC 2.0 errors

# See: https://www.jsonrpc.org/specification#error_object
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR_MIN = -32000
SERVER_ERROR_MAX = -32099

# Our own errors.
# TODO
