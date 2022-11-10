"""
A client for KBase Dynamic Services.

It utilizes a KBase "Generic Client" to implement the actual JSON-RPC calls,
focussing on the obtaining and caching the URL for a given service module.

Classes:
    URLCache
    DynamicServiceClient

Misc variables:
    DEFAULT_TIMEOUT
    DEFAULT_CACHE_LIFETIME
"""

import time
from lib.GenericClient import GenericClient

# Default timeout for upstream calls is 10 minutes; propagated to
# the generic client. This may seem like a long time (and it is!), but
# sometimes our services can be very slow. Generally timeouts across
# KBase seem to converge on 1 minute, so it is likely that the call
# will return with an error before DEFAULT_TIMEOUT.
DEFAULT_TIMEOUT = 600

# Default lifetime for cached urls is 5 minutes.
DEFAULT_CACHE_LIFETIME = 300


class URLCache:
    """
    Stores url associated with an arbitrary string key for a limited time.

    Although this is really a general purpose string cache, we dedicate it to
    URLs for clarity. It is intended for use by the DynamicServiceClient to store
    the dynamically allocated URL for a service under a key which is the
    service's module name.
    The lifetime of the cache entry defaults to DEFAULT_CACHE_LIFETIME, defined
    in this module, which may be overridden for an instance of this class, as well
    as per cache entry.
    Note that this class does not provide logic for cache entry refreshing. That logic
    needs to be handled by the caller, by noticing that a cache entry is None, and
    re-fetching the cached value, and repopulating the cache entry.

    ttl: Integer
        The "time to live", or lifetime, of a cache entry.
    """
    _url_cache = dict()

    def __init__(self, ttl=DEFAULT_CACHE_LIFETIME):
        self.ttl = ttl

    def set_url(self, name, url, ttl=None):
        """
        Cache an url under the given name, with an optional "time to live" in seconds.
        """
        if ttl is None:
            ttl = self.ttl

        self._url_cache.set(name, {
            'created': time.time(),
            'ttl': ttl,
            'url': url
        })

    def get_url(self, name):
        """
        Retrieve an url stored under the given name if it is found,
        otherwise return None.
        """
        cache_entry = self._url_cache.get(name)
        if cache_entry is None:
            return None
        elapsed = time.time() - cache_entry['created']
        if elapsed > cache_entry['ttl']:
            del self._url_cache[name]
            return None
        return cache_entry['url']

#
#
#
global_url_cache = URLCache()


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
    def __init__(self, url=None, module=None, token=None,
                 service_ver=None,
                 cache_lifetime=DEFAULT_CACHE_LIFETIME,
                 timeout=None):
        self.service_wizard_url = url
        self.service_ver = service_ver
        self.module_name = module
        self.cache_lifetime = cache_lifetime
        self.cached_url = None
        self.last_fetched_at = None
        self.token = token
        self.timeout = timeout

    def call_func(self, method, params=None, timeout=None):
        timeout = timeout or self.timeout

        # If not cached or cache entry is expired, re-fetch the url from
        # the service wizard.
        service_url = self._get_url(timeout)

        client = GenericClient(module=self.module_name,
                               url=service_url,
                               token=self.token,
                               timeout=timeout)

        return client.call_func(method, params)

    def _get_url(self, timeout):
        url = global_url_cache.get_url(self.module_name)
        if url is not None:
            return url
        url = self._lookup_url(timeout)
        global_url_cache.set_url(self.module_name, url)
        return url

    def _lookup_url(self, timeout):
        service_wizard = GenericClient(module='ServiceWizard',
                                       url=self.service_wizard_url,
                                       token=self.token,
                                       timeout=timeout)

        params = {
            'module_name': self.module_name,
            'version': self.service_ver
        }
        result = service_wizard.call_func('get_service_status', params)
        return result['url']
