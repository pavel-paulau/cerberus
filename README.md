Requirements
------------

Python 3.3 is required for the project. Use `easy_install` or `pip` for third-party packages:

    pip install -r requirements.txt

Usage
-----

    python -m cerberus [-h] --pullers PULLERS --pushers PUSHERS hostname

For instance:

    python -m cerberus --pullers=60 --pushers=40 172.23.97.50
