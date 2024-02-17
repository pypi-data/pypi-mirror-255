# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase, skipUnless
from commonconf import settings, override_settings
from memcached_clients import PymemcacheClient
from pymemcache.exceptions import MemcacheError
import os


class PymemcacheCacheOfflineTests(TestCase):
    def setUp(self):
        self.client = PymemcacheClient()

    def test_invalid_method(self):
        self.assertRaises(AttributeError, self.client.fake)

    def test_default_settings(self):
        client = self.client.client
        self.assertEqual(client.default_kwargs.get("max_pool_size"), 10)
        self.assertEqual(client.default_kwargs.get("connect_timeout"), 2)
        self.assertEqual(client.default_kwargs.get("timeout"), 2)
        self.assertEqual(client.default_kwargs.get("default_noreply"), True)


@override_settings(MEMCACHED_SERVERS=[("127.0.0.1", "11211")],
                   MEMCACHED_MAX_POOL_SIZE=5,
                   MEMCACHED_TIMEOUT=3,
                   MEMCACHED_NOREPLY=False)
@skipUnless(os.getenv("LIVE_TESTS"), "Set LIVE_TESTS=1 to run tests")
class PymemcacheCacheLiveTests(TestCase):
    def setUp(self):
        self.client = PymemcacheClient()
        self.client.flush_all()

    def test_settings(self):
        client = self.client.client
        self.assertEqual(client.default_kwargs.get("max_pool_size"), 5)
        self.assertEqual(client.default_kwargs.get("connect_timeout"), 2)
        self.assertEqual(client.default_kwargs.get("timeout"), 3)
        self.assertEqual(client.default_kwargs.get("default_noreply"), False)

    def test_client(self):
        key = "abc"

        reply = self.client.set(key, 12345)
        self.assertTrue(reply)
        self.assertEqual(self.client.get(key), 12345)

        reply = self.client.set(key, ["a", "b", "c"])
        self.assertTrue(reply)
        self.assertEqual(self.client.get(key), ["a", "b", "c"])
