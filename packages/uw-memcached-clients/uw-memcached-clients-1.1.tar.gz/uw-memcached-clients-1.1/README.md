# uw-memcached-clients

[![Build Status](https://github.com/uw-it-aca/uw-memcached-clients/workflows/tests/badge.svg?branch=main)](https://github.com/uw-it-aca/uw-memcached-clients/actions)
[![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-memcached-clients/badge.svg?branch=main)](https://coveralls.io/github/uw-it-aca/uw-memcached-clients?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/uw-memcached-clients.svg)](https://pypi.python.org/pypi/uw-memcached-clients)
![Python versions](https://img.shields.io/pypi/pyversions/uw-memcached-clients.svg)

A wrapper around the pymemcache memcached client (https://github.com/pinterest/pymemcache),
configured to support connection pooling in a clustered memcached environment.

Installation:

    pip install uw-memcached-clients

To use this client, you'll need these settings in your application or script:

    # A list of tuples (hostname, port) or strings containing a UNIX socket path.
    MEMCACHED_SERVERS=[]

Optional settings:

    MEMCACHED_USE_POOLING=True
    MEMCACHED_MAX_POOL_SIZE=10
    MEMCACHE_CONNECT_TIMEOUT=2
    MEMCACHED_TIMEOUT=2
    MEMCACHE_NOREPLY=True

See examples for usage.  Pull requests welcome.
