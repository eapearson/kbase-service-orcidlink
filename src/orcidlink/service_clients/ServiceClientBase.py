from orcidlink.service_clients.ClientBase import ClientBase


class ServiceClientBase(ClientBase):
    module = None

    def __init__(self, url=None, token=None, timeout=None):
        super().__init__(url, token, timeout)
