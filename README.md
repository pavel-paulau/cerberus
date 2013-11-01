Requirements
------------

Python 3.3 is required for the project. Use `easy_install` or `pip` for third-party packages:

    pip install -r requirements.txt

Usage
-----

    python -m cerberus [-h]
                       [--rampup RAMPUP]
                       [--sleep SLEEP]
                       --pullers PULLERS
                       --pushers PUSHERS
                       --bulkpullers BULKPULLERS
                       --auth cookie|header
                       hostname

For instance:

    python -m cerberus --pullers=60 --pushers=40 172.23.97.50
