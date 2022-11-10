class KBaseAuthException(Exception):
    def __init__(self, message, upstream_error, exception_string):
        self.message = message
        self.upstream_error = upstream_error
        self.exception_string = exception_string
