=====================
RapidSMS Applications
=====================

.. module:: rapidsms.apps
.. module:: rapidsms.apps.base

RapidSMS applications are Django apps which contain custom logic for
processing incoming and outgoing messages. Any number of RapidSMS applications
can be used in a project.

Each RapidSMS application defines a class that extends from
``rapidsms.apps.base.AppBase``, kept in the ``app.py`` submodule of a Django
app. For example, we might create a simple application that replies 'pong'
after receiving the message 'ping':

.. code-block:: python
    :linenos:

    # In pingpongapp/app.py

    from rapidsms.apps.base import AppBase


    class PingPong(AppBase):

        def handle(self, msg):
            if msg.text == 'ping':
                msg.respond('pong')
                return True
            return False

The ``send`` and ``receive`` methods in the
:doc:`router api <topics/router/messaging>` abstract the logic needed for
routing messages to applications. The following example provides a simplified
overview of how this is done:

.. code-block:: python
    :linenos:

    from rapidsms.messages import IncomingMessage
    from rapidsms.models import Backend, Connection
    from rapidsms.router.base import BaseRouter
    from pingpongapp.app import PingPong


    backend = Backend.objects.create(name='fake-backend')
    connection = Connection.objects.create(backend=backend, identity='2223334444')

    # Create a new basic router and add our PingPong app to it.
    router = BaseRouter()
    router.add_app(PingPong)

    # Create a new incoming message.
    msg = IncomingMessage(connection, 'ping')

    # Route the incoming message through the router's applications.
    router.incoming(msg)

    # Inspect the message responses to see that our app handled the message.
    print msg.responses[0].text  # 'pong'

Application and router behavior in RapidSMS are intertwined. In this section,
we focus on the behavior specific to applications, with references to some key
areas where this behavior is tied in with the router. For more information
about routing messages through applications, see the
:doc:`router documentation <topics/router/index>`.

Application Discovery
=====================

A RapidSMS application is contained in a Django app. The router manages
application discovery and keeps a list of associated applications through
which to route incoming and outgoing messages.

``BaseRouter.add_app`` takes one argument that is either an ``AppBase``
subclass or the name of a RapidSMS application's containing Django app. If the
argument is the name of a Django app, the method looks in ``app_name.app`` for
an ``AppBase`` subclass. The method then instantiates the subclass and adds it
to the router's associated applications.

The included router, ``BlockingRouter``, loads applications upon
initialization. It calls ``add_app`` on each app listed in the optional
``apps`` argument or in ``settings.INSTALLED_APPS``.

Incoming Message Processing
===========================

In ``BaseRouter.incoming``, the incoming message is processed in five phases.
At each phase, the message is processed by the router's associated
applications in the order they are listed in the `apps` list property. Each
application provides code for executing the phase. There are hooks which allow
an application to filter out a message, skip phases, or stop further
processing.

.. IMPORTANT::
   The order which your router chooses applications to process messages is
   extremely important, because each application will have the opportunity to
   block subsequent applications from processing a message. ``BlockingRouter``
   adds applications to ``apps`` in the order that they are loaded, so
   incoming messages are processed by applications in the order they are
   listed in ``settings.INSTALLED_APPS``.

The logic for each phase is defined in a method of the same name in the
``AppBase`` class. By default, no action is taken at any phase. Each subclass
may choose to override any of the default methods to use custom logic on
incoming messages.

1. *filter* - **Optionally abort further processng of the incoming message.**
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
            if msg.text == "Congratulations, you've won $1000!":
                return True  # This message is probably spam and should not be
                             # processed any more.
            return False

2. *parse* - **Modify message in a way that is globally useful.** This phase
   is used to modify the incoming message in a way that could be useful to
   other applications. All messages that aren't filtered go through the
   *parse* phase of every application. No INSERTs or UPDATEs should be done
   during this phase.

   **Example**: An application adds metadata about phone number registration
   to each message.

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

4. *default* - **Execute a default action if no application returns True
   during the handle phase.** For example, an application might want to
   provide additional help text or a generic response if no other application
   has handled the message. The application can return ``True`` from this
   method in order to prevent the remaining applications from executing their
   *default* stage.

5. *cleanup* - **Clean up work from other phases.**

Outgoing Message Processing
===========================

In ``BaseRouter.outgoing``, outgoing messages are processed in a manner
similar to incoming messages, except only one phase, ``outgoing``, is defined.
The outgoing message is processed sequentially by the router's associated
applications. However, the applications are called in reverse order with
respect to the order they are called in ``BaseRouter.incoming``, so the first
application called to process an incoming message is the last application that
is called to process an outgoing message. If any application returns ``True``
during the ``outgoing`` phase, all further processing of the message will be
aborted.

The logic for the ``outgoing`` phase is defined in a method of the same name
in the ``AppBase`` class. By default, no action is taken during this phase.
Each subclass may choose to override the default method to use custom logic on
outgoing messages.

Router Events: ``start`` and ``stop``
=====================================

For historical reasons, each application can provide start-up and shut-down
logic in the ``start`` and ``stop`` methods, respectively. These methods are
called from ``BaseRouter`` when the router is started or stopped. However,
this behavior has never been enforced. A "stopped" router can still receive
messages and will route them to applications, even "stopped" applications. As
we move toward v1.0, we expect to remove these methods from ``BaseApp``.
