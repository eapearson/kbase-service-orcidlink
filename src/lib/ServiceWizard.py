from lib.GenericClient import GenericClient


class ServiceWizard:
    def __init__(self, url, token=None):
        self.url = url
        self.token  = token
        self.client = GenericClient(
            url=url, module="ServiceWizard", token=token, timeout=60
        )

    def get_service_status(self, module_name, version=None):
        try:
            result = self.client.call_func(
                "get_service_status",
                {
                    "module_name": module_name,
                    "version": version
                },
            )
            return result, None
        except Exception as e:
            return None, {"exception": e, "message": str(e)}


