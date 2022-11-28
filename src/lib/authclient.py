"""
Created on Aug 1, 2016

A very basic KBase auth client for the Python server.

@author: gaprice@lbl.gov
"""
import hashlib
import threading
import time

import requests


class TokenCache(object):
    """A basic cache for tokens."""

    MAX_TIME_SEC = 5 * 60  # 5 min

    lock = threading.RLock()

    def __init__(self, maxsize=2000):
        self.cache = {}
        self.maxsize = maxsize
        self.halfmax = maxsize / 2  # int division to round down

    def token_expired(self, cached_at):
        if time.time() - cached_at > self.MAX_TIME_SEC:
            return True
        return False

    def get_user(self, token):
        with self.lock:
            token_info = self.cache.get(token)
        if not token_info:
            return None

        username, cached_at = token_info
        if self.token_expired(cached_at):
            return None

        return username

    def encode_token(self, token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def add_valid_token(self, token, username):
        if not token:
            raise ValueError("Must supply token")
        if not username:
            raise ValueError("Must supply username")

        encoded_token = self.encode_token(token)
        with self.lock:
            self.cache[encoded_token] = [username, time.time()]
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

    def __init__(self, auth_url=None):
        """
        Constructor
        """
        if auth_url is None:
            raise ValueError("auth_url not provided to auth client")

        self.authurl = auth_url

        self.cache = TokenCache()

    def get_user(self, token: str):
        if not token:
            raise ValueError("Must supply token")

        username = self.cache.get_user(token)
        if username:
            return username

        data = {"token": token, "fields": "user_id"}

        response = requests.post(self.authurl, data=data)

        if not response.ok:
            try:
                err = response.json()
            except Exception:
                response.raise_for_status()
            # message = "Error connecting to auth service: {} {}\n{}\n{}".format(
            #     response.status_code, response.reason, err["error"]["message"], self.authurl
            # )
            # raise ValueError(message)

            appcode = err['error']['appcode']
            if appcode == 10020:
                raise KBaseAuthInvalidToken('Invalid token')
            elif appcode == 30000:
                raise KBaseAuthMissingToken('Missing token')
            else:
                raise KBaseAuthException(err['error']['message'])
            # raise KBaseAuthException(err['error']['appcode'], err['error']['apperror'], err['error']['message'])

        username = response.json()["user_id"]
        self.cache.add_valid_token(token, username)
        return username


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
