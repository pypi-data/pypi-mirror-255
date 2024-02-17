# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase, skipUnless
from commonconf import settings, override_settings
import pymemcache
import mock
import os


@skipUnless(os.getenv("DJANGO_TESTS"), "Set DJANGO_TESTS=1 to run tests")
class PymemcacheCacheBackendTests(TestCase):
    def setUp(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "memcached_clients.tests.django_settings")
        import django
        from django.conf import settings

        if hasattr(django, "setup"):
            django.setup()

    def test_cache_options(self):
        from django.core.cache import cache
        self.assertIsInstance(cache._cache, pymemcache.HashClient)
        self.assertIs(cache._cache.use_pooling, True)
        self.assertEqual(cache._cache.default_kwargs["max_pool_size"], 4)
        self.assertIs(cache._cache.default_kwargs["default_noreply"], False)
        self.assertIs(cache._cache.default_kwargs["serde"],
                      pymemcache.serde.pickle_serde)

    @mock.patch.object(pymemcache.HashClient, "disconnect_all")
    def test_cache_close(self, mock_close):
        from django.core.cache import cache
        cache.close()
        mock_close.assert_not_called()
