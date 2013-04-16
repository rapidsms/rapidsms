.. _provision_what:

What to Provision
-----------------

.. _a-good-basic-setup:

A Good Basic Setup
==================

Here are a recommended set of choices for deploying Django
apps. Most of these choices have alternatives, but in the absence of a
reason to use an alternative, these should work reasonably well in most cases.

Operating System
    `Ubuntu LTS server`_: Ubuntu because it's stable, it's free, and it's
    popular among developers, so any Django or Python software is likely to
    work well on it. LTS because of the long support guarantee, and server
    since we don't need costly graphical desktop environments on our
    servers.

Django version
    The latest released version: because it will be supported by security
    fixes for the longest time, compared to any older version, and Django
    has a history of putting out pretty stable releases. (Maybe wait a
    couple of weeks after a new release to see if there's a .1 release.)

Database
    `PostgreSQL`_: because it and MySQL are the most popular free databases, so
    it's well supported, and MySQL is lacking some features. For example,
    MySQL cannot perform schema changes in transactions, so if a schema
    migration fails in the middle, your data could be left in an indeterminate
    state.

Schema migration
    `South`_: because it's really the only choice available for schema migrations
    in Django.

RapidSMS Router
    :router:`DatabaseRouter`: because it has the most features.

Message queue server
    `RabbitMQ`_: because it's stable and popular.

Asynchronous task scheduler
    `Celery`_: see :ref:`why_celery`.

.. _Celery: http://www.celeryproject.org/
.. _PostgreSQL: http://www.postgresql.org/
.. _RabbitMQ: http://www.rabbitmq.com/
.. _South:  http://south.readthedocs.org/en/latest/
.. _Ubuntu LTS Server: http://www.ubuntu.com/business/server
