class ServiceError(Exception):
    def __init__(self, code=None, message=None, data=None):
        self.message = message
        self.code = code
        self.data = data
