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
                sorted_iems = sorted(list(self.cache.items()), key=(lambda v: v[1][1]))
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

    def get_user(self, token):
        if not token:
            raise ValueError("Must supply token")

        username = self.cache.get_user(token)
        if username:
            return username

        d = {"token": token, "fields": "user_id"}

        ret = requests.post(self.authurl, data=d)
        if not ret.ok:
            try:
                err = ret.json()
            except Exception:
                ret.raise_for_status()
            message = "Error connecting to auth service: {} {}\n{}\n{}".format(
                ret.status_code, ret.reason, err["error"]["message"], self.authurl
            )
            raise ValueError(message)

        username = ret.json()["user_id"]
        self.cache.add_valid_token(token, username)
        return username
