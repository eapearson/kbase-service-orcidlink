"""
Created on Aug 1, 2016

A very basic KBase auth client for the Python server.

@author: gaprice@lbl.gov
"""
import hashlib
import threading
import time

import requests

global_cache = None


class Cache(object):
    """A basic cache """

    lock = threading.RLock()

    def __init__(self, maxsize: int, item_lifetime: int):
        self.cache = {}
        self.item_lifetime = item_lifetime
        self.maxsize = maxsize
        self.halfmax = maxsize / 2  # int division to round down

    def is_expired(self, cached_at: int):
        return time.time() - cached_at > self.item_lifetime

    def get(self, key: str):
        encoded_key = self.encode_key(key)
        with self.lock:
            item = self.cache.get(encoded_key)

        if not item:
            return None
        value, cached_at = item
        if self.is_expired(cached_at):
            return None

        return value

    def encode_key(self, value: str):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def add(self, key: str, value: str):
        encoded_key = self.encode_key(key)
        with self.lock:
            self.cache[encoded_key] = [value, time.time()]
            if len(self.cache) > self.maxsize:
                sorted_items = sorted(list(self.cache.items()), key=(lambda v: v[1][1]))
                for i, (t, _) in enumerate(sorted_items):
                    if i <= self.halfmax:
                        del self.cache[t]
                    else:
                        break


class KBaseAuth(object):
    """
    A very basic KBase auth client for the Python server.
    """

    def __init__(self, auth_url: str = None, cache_max_size: int = None, cache_lifetime: int = None):
        """
        Constructor
        """
        if auth_url is None:
            raise TypeError("missing required named argument 'auth_url'")

        if cache_max_size is None:
            raise TypeError("missing required named argument 'cache_max_size'")

        if cache_lifetime is None:
            raise TypeError("missing required named argument 'cache_lifetime'")

        self.authurl = auth_url

        global global_cache

        if global_cache is None:
            global_cache = Cache(cache_max_size, cache_lifetime)

        self.cache = global_cache

    def get_token_info(self, token: str):
        if not token:
            raise TypeError("missing positional argument 'token'")

        token_info = self.cache.get(token)
        if token_info:
            return token_info

        response = requests.post(self.authurl, data={"token": token})

        if not response.ok:
            try:
                err = response.json()
            except Exception:
                # Note that here we are raising the default exception for the
                # requests library in the case that a deep internal server error
                # is thrown without an actual json response. In other words, the
                # error is not a JSON-RPC error thrown by the auth2 service itself,
                # but some truly internal server error.
                # Note that ALL errors returned by stock KBase JSON-RPC 1.1 servers
                # are 500.
                response.raise_for_status()

            # Make an attempt to handle a specific auth error
            appcode = err['error']['appcode']
            if appcode == 10020:
                raise KBaseAuthInvalidToken('Invalid token')
            elif appcode == 30000:
                raise KBaseAuthMissingToken('Missing token')
            else:
                raise KBaseAuthException(err['error']['message'])

        token_info = response.json()
        self.cache.add(token, token_info)
        return token_info

    def get_username(self, token: str):
        return self.get_token_info(token)["user_id"]


class KBaseAuthException(Exception):
    pass


class KBaseAuthMissingToken(KBaseAuthException):
    pass


class KBaseAuthInvalidToken(KBaseAuthException):
    pass

# class KBaseAuthException(Exception):
#     def __init__(self, code: int, message: str, long_message: str):
#         super().__init__(message)
#         self.code = code
#         self.message = message
#         self.long_message = long_message
#
#     def to_dict(self):
#         return {
#             'code': self.code,
#             'message': self.message,
#             'long_message': self.long_message
#         }
