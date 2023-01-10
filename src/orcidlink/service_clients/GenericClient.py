from orcidlink.service_clients.ClientBase import ClientBase


class GenericClient(ClientBase):
    def __init__(self, module=None, url=None, token=None, timeout=None):
        super().__init__(url, token, timeout)
        # Required parameters
        if module is None:
            raise TypeError('The "module" argument is required')
        self.module = module
