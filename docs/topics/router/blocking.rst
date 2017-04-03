.. module:: rapidsms.router.blocking
.. router:: BlockingRouter

BlockingRouter
==============

.. versionadded:: 0.10.0

The :router:`BlockingRouter` is the most basic and easy to use router included
with RapidSMS. For this reason it is also the default router. As its name
suggests, :router:`BlockingRouter` handles messages synchronously (within the
main HTTP thread), waiting for application and backend processing to complete
before continuing. This is acceptable for many scenarios, but will be less
efficient if your project needs to handle many inbound and outbound messages.


Installation
------------

Set :setting:`RAPIDSMS_ROUTER` to use :router:`BlockingRouter`::

    RAPIDSMS_ROUTER = "rapidsms.router.blocking.BlockingRouter"

That's it!


How it works
------------

By default, :router:`BlockingRouter` automatically adds apps and backends
defined in your settings file via :setting:`INSTALLED_APPS` and
:setting:`INSTALLED_BACKENDS`. If you instantiate a :router:`BlockingRouter`,
you can see the available apps and backends::

    >>> from rapidsms.router.blocking import BlockingRouter
    >>> router = BlockingRouter()
    >>> router.apps
    [<app: handlers>, <app: default>, <app: messagelog>]
    >>> router.backends
    {'message_tester': <backend: message_tester>}

In this scenario, these settings were used::

    INSTALLED_APPS = [
        # trimmed to only show the relevant apps
        "rapidsms.contrib.handlers",
        "rapidsms.contrib.default",
        "rapidsms.contrib.messagelog",
    ]

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend.HttpTesterCacheBackend",
        },
    }


Implementation
--------------

:router:`BlockingRouter` is the default router, but it is also the base
router for all RapidSMS routers. :router:`CeleryRouter` and
:router:`DatabaseRouter` extend :router:`BlockingRouter` and override necessary
functionality. A subset of its methods are outlined below:

.. autoclass:: rapidsms.router.blocking.BlockingRouter
    :members: incoming_phases,outgoing_phases,add_app,get_app,add_backend,
              receive_incoming,send_outgoing,new_incoming_message,
              new_outgoing_message

.. class:: rapidsms.router.blocking.router.BlockingRouter

    is the full name for :py:class:`rapidsms.router.blocking.BlockingRouter`.
