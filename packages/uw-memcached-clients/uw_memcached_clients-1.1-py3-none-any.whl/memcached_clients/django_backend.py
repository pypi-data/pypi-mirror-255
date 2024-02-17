# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.cache.backends.memcached import BaseMemcachedCache


class PymemcacheCache(BaseMemcachedCache):
    """
    Implementation of a pymemcache binding for Django 2.x.
    """
    def __init__(self, server, params):
        import pymemcache
        super().__init__(server, params, library=pymemcache,
                         value_not_found_exception=KeyError)

    @property
    def _cache(self):
        if getattr(self, "_client", None) is None:
            kwargs = {
                "allow_unicode_keys": True,
                "default_noreply": False,
                "serde": self._lib.serde.pickle_serde,
            }
            kwargs.update(self._options)
            self._client = self._lib.HashClient(self._servers, **kwargs)
        return self._client

    def close(self, **kwargs):
        # Don't call disconnect_all() if connection pooling is enabled,
        # as it resets the failover state and creates unnecessary reconnects.
        if not self._cache.use_pooling:
            self._cache.disconnect_all()
