cerberus
========

[Sync Gateway](http://docs.couchbase.com/sync-gateway/) workload generator (prototype).


Requirements
------------

* Python 3.3

Third-party packages:

    pip install -r requirements.txt

Usage
-----

    python -m cerberus [-h] --pullers PULLERS --pushers PUSHERS hostname

For instance:

    python -m cerberus --pullers=60 --pushers=40 172.23.97.50
