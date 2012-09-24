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

.. versionadded:: 0.10.0

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

.. _custom-router:

Using a custom router
---------------------

While RapidSMS includes support for a number of routers out-of-the-box,
sometimes you might want to use a customized router. To use an external router
with RapidSMS, use the Python import path to the router class for the
:setting:`ROUTER` setting, like so::

    RAPIDSMS_ROUTER = 'path.to.router'

If you're building your own router, you can use the standard routers
as reference implementations.

Please see :doc:`Community Routers <community>` for a list of community-
maintained routers.
