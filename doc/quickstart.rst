Quick Start
===========

Installation
------------

You can install the linter from the source code

.. parsed-literal::

    git clone |url|
    cd |project|
    git checkout |version|
    python setup.py install

Usages
------

.. literalinclude:: help.txt

Standard use case looks pretty simple:

.. parsed-literal::

    |command| /path/to/git/repository

.. warning:: URL to a remote is not supported. Passing |url| as the argument will fail.
