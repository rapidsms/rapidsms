================
RapidSMS Routers
================

.. module:: rapidsms.router
.. module:: rapidsms.router.base
.. module:: rapidsms.router.blocking

The router is the message processing component of RapidSMS. It provides the
infrastructure to receive incoming and send outgoing messages, and triggers a
series of phases through which :doc:`applications
</topics/applications/index>` process messages. Each RapidSMS project can use
exactly one router, which should be chosen based on the needs of the project.

Application and router behavior in RapidSMS are intertwined. In this section,
we focus on the behavior specific to the router, with references to some key
areas where this behavior is tied to applications. For more information about
processing messages in applications, see the :doc:`applications documentation
</topics/applications/index>`.

.. _router-choice:

Choosing a Router
=================

Each RapidSMS project can use exactly one router, which should be chosen based
on the needs of the project. The path to your chosen router must go in the
:setting:`RAPIDSMS_ROUTER` setting::

    RAPIDSMS_ROUTER = 'path.to.your.RouterClass'

The default router is ``rapidsms.router.blocking.BlockingRouter``.

The choice of router is an important decision that will affect your message
processing performance. For example, some routers are easy to set up but will
struggle with large message volumes. More complex routers may process messages
more efficiently, but require more work to set up.

.. _discovery:

Application and Backend Discovery
=================================

The router maintains a collection of related :doc:`applications
</topics/applications/index>` through which it routes incoming and outgoing
messages, as well as a collection of :doc:`backends </topics/backends/index>`
through which it can send outgoing messages. Applications and backends can be
added manually by the user, or managed by the router implementation. For
example, ``BlockingRouter`` loads them upon initialization.

.. _application-discovery:

Applications
------------
``BaseRouter.add_app`` takes one argument that is either an ``AppBase``
subclass or the name of a RapidSMS application's containing Django app. If the
argument is the name of a Django app, the method looks in ``app_name.app`` for
an ``AppBase`` subclass to use. The method then instantiates the subclass and
adds it to the router's list of associated applications, ``apps``.

.. _backend-discovery:

Backends
--------
TODO: ``BaseRouter.add_backend``

Message Processing
==================

In general, the ``send`` and ``receive`` methods in the :doc:`messaging api
</topics/router/messaging>` abstract the logic needed for passing messages to
the router. In the ``incoming`` and ``outgoing`` router methods, messages are
passed to the router's associated applications for processing.

.. _router-incoming:

Incoming Messages
-----------------

.. NOTE::
   See also the :ref:`application documentation on incoming message processing
   <application-incoming>`.

In ``BaseRouter.incoming``, the incoming message is processed in five phases.
Each application provides code for executing the phases. The router method
defines hooks which allow an application to filter out a message, skip phases,
or stop further processing.

1. :ref:`filter <phase-filter>` - **Optionally abort all further processing of
   the incoming message (including cleanup).**
2. :ref:`parse <phase-parse>` - **Modify the message in a way that is globally
   useful.**
3. :ref:`handle <phase-handle>` - **Respond to the incoming message.**
4. :ref:`default <phase-default>` - **Execute a default action if no
   application returns true during the handle phase.**
5. :ref:`cleanup <phase-cleanup>` - **Clean up work from previous phases.**

The order in which the router chooses applications to process messages is
extremely important, because each application will have the opportunity to
block subsequent applications from processing a message. In
``BaseRouter.incoming``, the message is processed by applications in the order
they are listed in the ``apps`` list property. For ``BlockingRouter``, this
means that messages are processed by applications in the order they are listed
in :setting:`INSTALLED_APPS`.

.. _router-outgoing:

Outgoing Messages
-----------------

.. NOTE::
   See also the :ref:`application documentation on outgoing message
   processing <application-outgoing>`.

In ``BaseRouter.outgoing``, the outgoing message is processed sequentially by
the applications listed in the ``apps`` list property. However, the
applications are called in reverse order with respect to the order they are
called in ``BaseRouter.incoming``, so the first application called to process
an incoming message is the last application that is called to process an
outgoing message. If any application returns ``True`` during the *outgoing*
phase, all further processing of the message will be aborted.

.. _router-types:

Router Types
============

All routers should extend from ``rapidsms.router.base.BaseRouter``. The
``BaseRouter`` is a fully-functional router that provides basic
implementations of all router methods. Subclasses may override the default
methods to enhance convenience or optimize performance.

.. _blocking-router:

BlockingRouter
--------------

.. versionadded:: 0.10.0

RapidSMS provides an easy-to-use default router at
``rapidsms.router.blocking.BlockingRouter``. As its name suggests,
``BlockingRouter`` handles messages synchronously, waiting for all application
and backend processing to complete before continuing. This is acceptable for
many scenarios, but will be less efficient if your project needs to handle
many inbound and outbound messages.

``BlockingRouter`` adds apps and backends upon initialization. By default,
it searches for relevant classes in the Django apps in
:setting:`INSTALLED_APPS` and :setting:`INSTALLED_BACKENDS`. Alternatively,
you may provide specific classes or Django apps in which to search in the
``apps`` and ``backends`` list arguments. To illustrate::

    >>> from django.conf import settings
    >>> from rapidsms.router.blocking import BlockingRouter
    >>> print settings.INSTALLED_APPS
    ['rapidsms.contrib.handlers', 'rapidsms.contrib.default',
    'rapidsms.contrib.locations', 'rapidsms.contrib.messagelog',
    ... (other Django apps) ...]
    >>> print settings.INSTALLED_BACKENDS
    {'message_tester': {'ENGINE': 'rapidsms.contrib.httptester.backend'}}
    >>> router = BlockingRouter()
    >>> router.apps
    [<app: handlers>, <app: default>, <app: locations>, <app: messagelog>]
    >>> router.backends
    {'message_tester': <backend: message_tester>}

``BlockingRouter`` also overrides ``BaseRouter.incoming`` to automatically
handle (via the ``outgoing`` method) responses to the incoming message.

.. _custom-router:

Custom Routers
--------------

While RapidSMS includes support for a number of routers out-of-the-box,
sometimes you might have need for a customized router. If you're building your
own router, you can use the standard routers as reference implementations.

Please see :doc:`Community Routers <community>` for a directory of
community-maintained routers that might be useful in your project.
