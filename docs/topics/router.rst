======
Router
======

.. module:: rapidsms.router

A router is the message processing component of RapidSMS. It provides the
infrastrcture to receive incoming and send outgoing messages. Generally, every
RapidSMS project uses a router and you can chose which router to use based on
the needs of your project.

The basics:

* You may use any router, but only one router can be used per project.

* Each router contains a collection of related apps and backends.

* All routers will trigger a set of phases for your apps to use and hook into.

Choosing a router
=================

Most routers require a small amount of setup. To start, you need to tell
RapidSMS which router you want to use. This is an important decision that
affects your message processing performance. Some routers are easy to setup,
but will struggle with large message volumes. More complex routers can process
messages more efficiently, but require more work to setup.

Your router preference goes in the :setting:`RAPIDSMS_ROUTER` setting in your
settings file. Here's an explanation of all available values for
:setting:`RAPIDSMS_ROUTER`.

BlockingRouter
--------------

.. versionadded:: 0.9.7

The ``BlockingRouter`` is the most basic and easy to use router included with
RapidSMS. For this reason it is also the default router. As it's name suggests,
``BlockingRouter`` handles messages synchronously, waiting for app and backend
proceessing to complete before continuing. This is acceptable for many
scenarios, but will be less efficient if your project needs to handle many
inbound and outbound messages.

``BlockingRouter`` can be used by setting :setting:`RAPIDSMS_ROUTER` to the
following::

    RAPIDSMS_ROUTER = 'rapidsms.router.blocking.BlockingRouter'

By default, ``BlockingRouter`` automatically adds apps and backends defined in
your settings file via :setting:`INSTALLED_APPS` and
:setting:`INSTALLED_BACKENDS`. If you instaniate a ``BlockingRouter``, you can
see the available apps and backends::

    >>> from rapidsms.router.blocking import BlockingRouter
    >>> router = BlockingRouter()
    >>> router.apps
    [<app: handlers>, <app: default>, <app: locations>, <app: messagelog>]
    >>> router.backends
    {'message_tester': <backend: message_tester>}

In this scenario, these settings were used::

    INSTALLED_APPS = [
        # trimmed to only show the relavent apps
        "rapidsms.contrib.handlers",
        "rapidsms.contrib.default",
        "rapidsms.contrib.locations",
        "rapidsms.contrib.messagelog",
    ]

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
    }

LegacyRouter
------------

.. versionadded:: 0.9.7

The ``LegacyRouter`` is a port of the default (and only) router in RapidSMS
0.9.6a and earlier.

.. note::

    The ``LegacyRouter`` uses Python's `threading
    <http://docs.python.org/library/threading.html>`_ module to encapsulate
    backends into indepedent threads. Using this model, backends can operate
    independently from one another, blocking for I/O and waiting for external
    service calls. Many of the original backends operated in this way. For example,
    ``rapidsms.backends.http`` started a `HTTP server
    <https://github.com/rapidsms/rapidsms/blob/
    a7a0fccffa582d5c3cd320bd659cd2bd95785a51/lib/rapidsms/backends/http.py>`_ to
    listen on a specified port and ``rapidsms.backends.gsm`` communicated directly
    with a `GSM modem
    <https://github.com/rapidsms/rapidsms/blob/a7a0fccffa582d5c3cd320
    bd659cd2bd95785a51/lib/rapidsms/backends/gsm.py>`_. While this method provided RapidSMS with a routing architecture, the need for a pluggable system grew due to the following reasons:

    * Thread interaction was complicated and not always intuitive.
    * If the route process died unexpectedly, all backends (and hence message  processing) were brought offline.
    * Automated testing was difficult and inefficient, because the router (and all its threads) needed to be started/stopped for each test.

``LegacyRouter`` can be used by setting :setting:`RAPIDSMS_ROUTER` to the
following::

    RAPIDSMS_ROUTER = 'rapidsms.router.legacy.LegacyRouter'

Once configured, you use the ``runrouter`` management command (in a separate
shell from ``runserver``, if developing locally) to start the router. For
example::

    $ ./manage.py runrouter
    [legacyrouter]: Starting RapidSMS...
    ...

Using a custom router
---------------------

While RapidSMS includes support for a number of routers out-of-the-box,
sometimes you might want to use a customized router. To use an external router
with RapidSMS, use the Python import path to the router class for the
:setting:`ROUTER` setting, like so::

    RAPIDSMS_ROUTER = 'path.to.router'

If you're building your own router, you can use the standard routers
as reference implementations.
