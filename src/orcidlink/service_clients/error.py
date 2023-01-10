class ServiceError(Exception):
    def __init__(self, code=None, name=None, message=None, data=None):
        super().__init__(message)
        self.message = message
        self.name = name
        self.code = code
        self.data = data


# See: https://www.jsonrpc.org/specification#error_object
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32603
INTERNAL_ERROR = -32603
SERVER_ERROR_MIN = -32000
SERVER_ERROR_MAX = -32099
