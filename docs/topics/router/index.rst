================
RapidSMS Routers
================

.. module:: rapidsms.router
.. module:: rapidsms.router.base
.. module:: rapidsms.router.blocking

The router is the message processing component of RapidSMS. It provides the
infrastructure and defines the workflow to receive, process and send text
messages. Each RapidSMS project can use only one router, which should be chosen
based on the needs of the project.

The basics:

* You may use any router, but only one router can be used per project.
* Each router contains a collection of installed apps and backends.
* All routers will trigger a set of phases for message processing.

Application and router behavior in RapidSMS are intertwined. In this section,
we focus on the behavior specific to the router, with references to some key
areas where this behavior is tied to applications. For more information about
processing messages in applications, see the :doc:`applications documentation
</topics/applications/index>`.


.. _router-choice:

Choosing a Router
=================

Each RapidSMS project can use only one router, which should be chosen based
on the needs of the project. The path to your chosen router must go in the
:setting:`RAPIDSMS_ROUTER` setting::

    RAPIDSMS_ROUTER = 'path.to.your.RouterClass'

The default router is ``rapidsms.router.blocking.BlockingRouter``.

The choice of router is an important decision that will affect your message
processing performance. For example, some routers are easy to set up but will
struggle with large message volumes. More complex routers may process messages
more efficiently, but require more work to set up.


Supplied Routers
-----------------

RapidSMS includes several routers for you to use:

* :router:`BlockingRouter` - Default router that processes messages synchronously within the HTTP thread.
* :router:`CeleryRouter` - Celery-enabled router that processes messages asynchronously.
* :router:`DatabaseRouter` - Database, Celery-enabled router that queues messages in the database for asynchronous processing.

If you can't find a router that's suitable for your needs, you can write a custom router.


Using a custom router
---------------------

While RapidSMS includes support for a number of routers out-of-the-box,
sometimes you may want to use a customized router. To use a custom router
with RapidSMS, use the dotted Python path to the router class for the
:setting:`RAPIDSMS_ROUTER` setting, like so::

    RAPIDSMS_ROUTER = 'path.to.RouterClass'

If you're building your own router, you can use the standard routers
as reference implementations. All routers should extend from :class:`BlockingRouter <rapidsms.router.blocking.BlockingRouter>`.


.. _discovery:

Applications and Backends
=========================

While the router provides the foundation for messaging processing, applications and backends actually perform the message processing:

* **Applications:** The router maintains a collection of related :doc:`applications </topics/applications/index>` through which it routes incoming and outgoing messages. Applications are defined in :setting:`INSTALLED_APPS` and loaded, by default, when the router is instantiated via :meth:`add_app <rapidsms.router.blocking.BlockingRouter.add_app>`.
* **Backends:** The router also maintains a collection of related :doc:`backends </topics/backends/index>` to send outgoing messages. Backends are defined in :setting:`INSTALLED_BACKENDS` and loaded, by default, when the router is instantiated via :meth:`add_backend <rapidsms.router.blocking.BlockingRouter.add_backend>`.


Message Processing
==================

The :doc:`Messaging API </topics/router/messaging>` defines :func:`send
<rapidsms.router.send>` and :func:`receive <rapidsms.router.receive>` to route
messages through the router. Messages are processed via a series of phases, depending on direction. These phases are outlined below.


.. _router-incoming:

Incoming Messages
-----------------

.. NOTE::
   See also the :ref:`application documentation on incoming message processing
   <application-incoming>`.

Incoming messages are processed in five phases. Each application provides code
for executing the phases. The router method defines hooks which allow an
application to filter out a message, skip phases, or stop further processing.

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
block subsequent applications from processing a message. :meth:`receive_incoming <rapidsms.router.blocking.BlockingRouter.receive_incoming>` processes messages in the order they are listed in :setting:`INSTALLED_APPS`.


.. _router-outgoing:

Outgoing Messages
-----------------

.. NOTE::
   See also the :ref:`application documentation on outgoing message
   processing <application-outgoing>`.

:meth:`send_outgoing <rapidsms.router.blocking.BlockingRouter.send_outgoing>`
processes messages sequentially, in the order they are listed in
:setting:`INSTALLED_APPS`. However, the applications are called in reverse
order, so the first application called to process an incoming message is the
last application that is called to process an outgoing message. If any
application returns ``True`` during the *outgoing* phase, all further
processing of the message will be aborted.
