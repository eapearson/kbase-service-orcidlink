"""
A client for KBase Dynamic Services.

It utilizes a KBase "Generic Client" to implement JSON-RPC calls to services
whose services are registered with the dynamic service service.

Classes:
    URLCache
    DynamicServiceClient

Misc variables:
    DEFAULT_CACHE_TTL
"""

from cache3 import SafeCache
from orcidlink.service_clients.GenericClient import GenericClient

# Default lifetime for cached urls is 5 minutes.
DEFAULT_CACHE_TTL = 300

DEFAULT_CACHE_MAX_SIZE = 100

GLOBAL_URL_CACHE = None


class DynamicServiceClient:
    """
    A JSON-RPC 1.1 client operating against dynamic services managed by KBase.

    A "dynamic service" is one that is registered with the catalog, and whose url is
    dynamically allocated, although in practice is stable for a given git hash for the
    service repo.

    We won't describe that whole mechanism, but note that this class utilizes the "Service Wizard"
    service to determine and cache the url for a given dynamic service, as identified
    by its module name, and otherwise operates just like the Generic Client.
    """

    def __init__(
            self,
            # required
            url=None,
            module=None,
            timeout=None,
            # optional
            token=None,
            version=None,
            cache_ttl=DEFAULT_CACHE_TTL,
            cache_max_size=DEFAULT_CACHE_MAX_SIZE
    ):
        #
        # Required parameters
        #
        if url is None:
            raise TypeError('The "url" named argument is required')
        self.service_wizard_url = url

        if timeout is None:
            raise TypeError('The "timeout" named argument is required')
        # Note that we operate with ms time normally, but httpx uses
        # seconds float.
        self.timeout = timeout

        if module is None:
            raise TypeError('The "module" named argument is required')
        self.module_name = module

        #
        # Optional parameters
        #

        self.version = version
        self.cache_ttl = cache_ttl
        self.cache_max_size = cache_max_size
        self.token = token

        #
        # attributes not from parameters
        #
        self.cached_url = None
        self.last_fetched_at = None

        self._initialize_cache()

    # Private

    def _initialize_cache(self, force=False):
        global GLOBAL_URL_CACHE
        if GLOBAL_URL_CACHE is None or force:
            GLOBAL_URL_CACHE = SafeCache(max_size=self.cache_max_size, timeout=self.cache_ttl)

    def _get_url(self, timeout):
        key = f"{self.module_name}:{self.version or 'null'}"
        item = self._cache().get(key)
        if item is not None:
            return item["url"]
        url = self._lookup_url(timeout)
        self._cache().set(key, {"url": url})
        return url

    def _lookup_url(self, timeout):
        timeout = timeout or self.timeout
        service_wizard = GenericClient(
            module="ServiceWizard",
            url=self.service_wizard_url,
            token=self.token,
            timeout=timeout,
        )

        params = {"module_name": self.module_name, "version": self.version}
        result = service_wizard.call_func("get_service_status", params)
        return result["url"]

    # Public

    def call_func(self, method, params=None, timeout=None):
        timeout = timeout or self.timeout

        # If not cached or cache entry is expired, re-fetch the url from
        # the service wizard.
        service_url = self._get_url(timeout)

        client = GenericClient(
            module=self.module_name, url=service_url, token=self.token, timeout=timeout
        )

        return client.call_func(method, params)

    @staticmethod
    def _cache():
        global GLOBAL_URL_CACHE
        return GLOBAL_URL_CACHE

    @staticmethod
    def clear_cache():
        global GLOBAL_URL_CACHE
        if GLOBAL_URL_CACHE is not None:
            GLOBAL_URL_CACHE.clear()
