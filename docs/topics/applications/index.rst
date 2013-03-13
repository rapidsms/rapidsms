=====================
RapidSMS Applications
=====================

.. module:: rapidsms.apps
.. module:: rapidsms.apps.base

RapidSMS applications are Django apps which contain custom logic for
processing incoming and outgoing messages. When the :doc:`router
</topics/router/index>` receives an incoming or outgoing message, it triggers
a series of phases through which its associated applications can process the
message. Any number of RapidSMS applications can be used in a project.

Each RapidSMS application defines a class that extends from
``rapidsms.apps.base.AppBase``, kept in the ``app.py`` submodule of a Django
app. The Django app also contains models, views, and methods required by the
application.

As an example, we might create a simple application that replies 'pong' after
receiving the message 'ping':

.. code-block:: python
    :linenos:

    # In pingpongapp/app.py

    from rapidsms.apps.base import AppBase


    class PingPong(AppBase):

        def handle(self, msg):
            """Handles incoming messages."""
            if msg.text == 'ping':
                msg.respond('pong')
                return True
            return False

After associating the PingPong application with the router, new incoming and
outgoing messages received by the router are passed through the application for
processing. All incoming 'ping' messages will receive a 'pong' reply. In
general, the ``send`` and ``receive`` methods in the :doc:`messaging api
</topics/router/messaging>` abstract the logic needed for passing messages to
the router.

Application and router behavior in RapidSMS are intertwined. In this section,
we focus on the behavior specific to applications, with references to some key
areas where this behavior is tied to the router. For more information about
routing messages through applications, see the :doc:`router documentation
</topics/router/index>`.

.. _application-structure:

Application Structure
=====================

A RapidSMS application is contained in a Django app. Each application defines
a class that extends from ``rapidsms.apps.base.AppBase``, kept in the
``app.py`` submodule of the Django app.

The router maintains a collection of associated applications through which to
route incoming and outgoing messages. :ref:`Application discovery
<application-discovery>` is managed through the ``BaseRouter.add_app`` method.
The default router, ``BlockingRouter``, loads applications upon initialization
by calling ``BaseRouter.add_app`` on each app listed in the optional ``apps``
argument or in :setting:`INSTALLED_APPS`.

.. _application-incoming:

Incoming Message Processing
===========================

.. NOTE::
   See also the :ref:`router documentation on incoming message processing
   <router-incoming>`.

The router receives each incoming message through its ``incoming`` method. In
``BaseRouter.receive_incoming``, the message is passed sequentially to the
router's associated applications in each of five processing phases.
Applications provide the code to execute each phase. The router provides hooks
which allow an application to filter out a message, skip phases, or stop
further processing.

.. IMPORTANT::
   The order in which the router chooses applications to process messages is
   extremely important, because each application will have the opportunity to
   block subsequent applications from processing a message.

The logic for each phase is defined in a method of the same name in the
``AppBase`` class. By default, no action is taken at any phase. Each subclass
may choose to override any of the default methods to use custom logic on
incoming messages.

.. _phase-filter:

1. *filter* - **Optionally abort further processing of the incoming message.**
   The *filter* phase is executed before any other processing or modification
   of the incoming message. If an application returns ``True`` from this
   phase, the message is filtered out and no further processing will be done
   by any application (not even *cleanup*).

   **Example**: An application that filters out spam messages:

.. code-block:: python
    :linenos:

    from rapidsms.apps.base import AppBase

    class SpamFilter(AppBase):

        def filter(self, msg):
            """Filter out spam messages."""
            if msg.text == "Congratulations, you've won a free iPod!":
                return True  # This message is probably spam and should not be
                             # processed any more.
            return False

.. _phase-parse:

2. *parse* - **Modify message in a way that is globally useful.** This phase
   is used to modify the incoming message in a way that could be useful to
   other applications. All messages that aren't filtered go through the
   *parse* phase of every application. No INSERTs or UPDATEs should be done
   during this phase.

   **Example**: An application adds metadata about phone number registration
   to each message.

.. _phase-handle:

3. *handle* - **Respond to the incoming message.** The router passes incoming
   messages through the *handle* phase of each application until one of them
   returns ``True``. All subsequent apps will not handle the message.

   It is considered best practice to return ``True`` during the *handle* phase
   if the application responds to or otherwise alters the message. Although an
   application may return ``False`` in order to allow other applications to
   handle the message, remember that the *default* phase will execute if no
   application returns ``True`` during *handle*.

   As mentioned above, the order in which the router chooses to send messages
   to applications is very important. For example, you may wish to have
   'keyword' applications (which look for a specific trigger word) handle a
   message before more general applications that use a regex to match possible
   text.

.. _phase-default:

4. *default* - **Execute a default action if no application returns True
   during the handle phase.** For example, an application might want to
   provide additional help text or a generic response if no other application
   has handled the message. The application can return ``True`` from this
   method in order to prevent the remaining applications from executing their
   *default* stage.

.. _phase-cleanup:

5. *cleanup* - **Clean up work from previous phases.**

.. _application-outgoing:

.. _phase-outgoing:

Outgoing Message Processing
===========================

.. NOTE::
   See also the :ref:`router documentation on outgoing message processing
   <router-outgoing>`.

The router receives each outgoing message through its ``outgoing`` method.
Messages are processed in a manner similar to incoming messages, except only
one phase, *outgoing*, is defined. In ``BaseRouter.send_outgoing``, the message
is processed sequentially by the router's associated applications. However, the
applications are called in reverse order with respect to the order they are
called in ``BaseRouter.receive_incoming``, so the first application called to
process an incoming message is the last application that is called to process
an outgoing message. If any application returns ``True`` during the *outgoing*
phase, all further processing of the message will be aborted.

The logic for the *outgoing* phase is defined in a method of the same name
in the ``AppBase`` class. By default, no action is taken during this phase.
Each subclass may choose to override the default method to use custom logic on
outgoing messages.

.. _router-events:

Router Events: ``start`` and ``stop``
=====================================

For historical reasons, each application can provide start-up and shut-down
logic in the ``start`` and ``stop`` methods, respectively. These methods are
called from ``BaseRouter`` when the router is started or stopped. However,
this behavior has never been enforced. A "stopped" router can still receive
messages and will route them to applications, even "stopped" applications. As
we move toward v1.0, we expect to remove these methods from ``BaseApp``.

.. _scheduling:

Scheduling tasks
================

If your application needs to run tasks asynchronously, either on-demand
or on a schedule, you can of course use any mechanism that works in Django.
The RapidSMS project recommends using Celery, and there are some advantages
to using Celery in RapidSMS applications compared to other schedulers.
See :doc:`Using Celery for Scheduling Tasks </topics/celery>`

.. _other-applications:

Contrib and Community Applications
==================================

There are many existing RapidSMS applications. The applications in
``rapidsms.contrib`` are maintained by core developers and provide
broad-reaching functionality that will be useful to many developers. We also
provide a :doc:`directory </topics/applications/community>` of
community-maintained RapidSMS applications that may be useful in your project.
