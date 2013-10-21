cerberus
========

[Sync Gateway](http://docs.couchbase.com/sync-gateway/) workload generator (prototype).


Prerequisites
-------------

* Python 3.3

Installation
------------

    pip install cerberus

Usage
-----

    cerberus [-h] --pullers PULLERS --pushers PUSHERS hostname

For instance:

    cerberus --pullers=60 --pushers=40 172.23.97.50

While developing:

    python -m cerberus.main --pullers=60 --pushers=40 172.23.97.50
