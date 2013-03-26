.. _database-backend:

====================
The Database Backend
====================

The database backend has a special purpose, and is primarily used
for testing. When the router sends an outgoing message via the
database backend, instead of sending a text message, the database
backend stores the message in a database table.

Configuring
-----------

To configure the database backend:

1. Add its class to the :setting:`INSTALLED_BACKENDS` setting:

.. code-block:: python
   :emphasize-lines: 4

    INSTALLED_BACKENDS = {
        ...
        "my-db-backend": {
            "ENGINE": "rapidsms.backends.db.outgoing.DatabaseBackend",
        },
        ...
    }

2. Add its app to :setting:`INSTALLED_APPS`:

.. code-block:: python
    :emphasize-lines: 3

    INSTALLED_APPS = [
        ...
        'rapidsms.backends.db',
        ...
    ]

3. Create its database table:

.. code-block:: bash

    ./manage.py syncdb

If you're using `South`_, you should run migrations:

.. code-block:: bash

    ./manage.py migrate


No URLs need to be configured, since the database backend cannot
receive messages from outside RapidSMS.

.. _South: http://south.readthedocs.org/en/latest/
