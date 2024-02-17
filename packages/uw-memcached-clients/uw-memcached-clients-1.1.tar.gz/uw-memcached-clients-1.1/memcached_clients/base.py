# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from pymemcache.exceptions import MemcacheError
from pymemcache import HashClient
from pymemcache import serde
from commonconf import settings
from threading import local
from logging import getLogger
import socket

logger = getLogger(__name__)


class PymemcacheClient():
    """
    A settings-based wrapper around pymemcache.
    """
    def __init__(self):
        self._local = local()

    def __getattr__(self, name, *args, **kwargs):
        """
        Pass unshimmed method calls through to the client, and add logging
        for errors.
        """
        def handler(*args, **kwargs):
            try:
                return getattr(self.client, name)(*args, **kwargs)
            except (MemcacheError, socket.gaierror) as ex:
                logger.error("memcached {}: {}".format(name, ex))
            except AttributeError:
                raise
        return handler

    @property
    def client(self):
        if not hasattr(self._local, "client"):
            self._local.client = self.__client__()
        return self._local.client

    def __client__(self):
        return HashClient(
            getattr(settings, "MEMCACHED_SERVERS", []),
            use_pooling=getattr(settings, "MEMCACHED_USE_POOLING", True),
            max_pool_size=getattr(settings, "MEMCACHED_MAX_POOL_SIZE", 10),
            connect_timeout=getattr(settings, "MEMCACHED_CONNECT_TIMEOUT", 2),
            timeout=getattr(settings, "MEMCACHED_TIMEOUT", 2),
            default_noreply=getattr(settings, "MEMCACHED_NOREPLY", True),
            serde=serde.pickle_serde)
