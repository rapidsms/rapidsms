=====================
RapidSMS Applications
=====================

.. module:: rapidsms.apps
.. module:: rapidsms.apps.base

RapidSMS applications are Django apps which hold the custom logic used to 
respond to incoming messages. Any number of RapidSMS applications can be used 
in a project.

Each RapidSMS application defines a class that extends from 
``rapidsms.apps.base.AppBase``, kept in the ``app.py`` file of a Django app. A 
simple application might look like this:

.. code-block:: python
    :linenos:

    # In myapp/app.py

    from rapidsms.apps.base import AppBase

    class App(AppBase):
        
        def handle(self, msg):
            msg.respond("Hello, world!")

RapidSMS application discovery is handled by the router.  When an incoming or 
outgoing message is received, the router calls a series of processing stages 
on each of its associated applications.

Application Discovery
=====================

A RapidSMS application is a Django app. The default router, 
``BlockingRouter``, loads RapidSMS applications upon initialization. It looks 
in the optional ``apps`` list argument or in ``settings.INSTALLED_APPS`` for 
any Django apps with an ``app.py`` file containing a class which extends from 
``AppBase.``

When the router receives an incoming or outgoing message, it routes the
message through the RapidSMS applications that it is aware of. The 
``BaseRouter`` routes messages to applications sequentially, in the order in 
which they were loaded.

Incoming Message Processing
===========================

In ``BaseRouter.incoming``, the incoming message is processed in the phases 
defined in the router's ``incoming_phases`` property.  At each phase, the 
message is processed sequentially by the router's associated applications. 
Each application provides code for executing the phase. There are hooks 
throughout the process which allow an application to filter a message, 
skip phases, or stop further processing.

.. IMPORTANT::
   The order which your router chooses applications to process messages is 
   extremely important. Each application which processes the message will have 
   the opportunity to prevent further applications from doing so.

Five incoming phase methods are defined in the ``AppBase`` class, and included 
in ``BaseRouter.incoming_phases``. By default, no action is taken at any 
phase. Each application subclass may override any of the base methods to use 
custom logic on incoming messages.

1. ``filter`` - **Optionally abort further processng of the incoming 
   message.** The *filter* phase is executed before any other processing or 
   modification of the incoming message. If an application returns ``True`` 
   from this phase, the message is filtered and no further processing will be 
   done by any application (not even *cleanup*).

   **Example**: An application filters out spam messages:

.. code-block:: python
    :linenos:

    from rapidsms.apps.base import AppBase

    class App(AppBase):

        def filter(self, msg):
            """Filter out spam messages."""
            if msg.text == "Congratulations, you've won $1000!":
                return True  # This message is probably spam and should not be 
                             # processed any more.
            return False

2. ``parse`` - **Modify message in a way that is globally useful.** This phase 
   is used to modify the incoming message in a way that could be useful to 
   other applications. All messages that aren't filtered go through the 
   *parse* phase of every application. No INSERTs or UPDATEs should be done at 
   this phase.

   **Example**: An application adds metadata about phone number registration 
   to each message.

3. ``handle`` - **Respond to the incoming message.** The router passes 
   incoming messages through the *handle* phase of each application until one 
   of them returns ``True``. All subsequent apps will not handle the message.

   Your router may or may not guarantee the order in which applications are 
   called to handle the message. The default router, ``BlockingRouter``, loads 
   in applications in the order they are listed in ``installed_apps``. This is 
   commonly exploited to load 'keyword' applications (those which look for a 
   specific trigger word) before more general applications that use a regex to
   match possible text.

   It is considered best practice to return ``True`` during the *handle* phase 
   if the application responds to or otherwise alters the message. Although an 
   application may return ``False`` in order to allow other applications to 
   handle the message, remember that the *default* phase will execute if no 
   application returns ``True`` during *handle*.

4. ``default`` - **Execute a default action if no application returns True 
   during the handle phase.** For example, an application might want to 
   provide additional help text or a generic response if no other application 
   has handled the message. The application can return ``True`` from this 
   method in order to prevent the remaining applications from executing their 
   *default* stage.

5. ``cleanup`` - **Clean up work from other phases.**

If you wish to define a separate phase, you must add a method with the phase 
name to the base class from which your applications extend and add the phase 
to your router's ``incoming_phases`` list. You may need to override the 
``incoming`` method of your router if your stage needs custom hooks.

Outgoing Message Processing
===========================

Outgoing messages are processed in a manner similar to incoming messages. In 
``BaseRouter.outgoing``, the outgoing message is processed in the phases 
defined in the router's ``outgoing_phases`` property. At each phase, the 
message is processed sequentially by the router's associated applications. The
applications are called in reverse of the order they are called during 
``BaseRouter.incoming``, so that the first application called for an incoming 
message is the last application called on an outgoing message. Each 
application provides code for executing the phase. By returning ``True`` from 
any outgoing phase, an application can abort all further processing of the 
message.

One outgoing phase is defined in the ``AppBase`` class, and included in 
``BaseRouter.outgoing_phases``. By default, no action is taken during this 
phase. Each application subclass may override the base method to use custom 
logic on outgoing messages.

Router Events: "Starting" and "Stopping"
========================================

For historical reasons, each application can provide start-up and shut-down 
logic in the ``start`` and ``stop`` methods, respectively. These methods are 
called from ``BaseRouter`` when the router is started or stopped. However, 
this behavior has never been enforced. A "stopped" router can still receive 
messages and will route them to applications, even "stopped" applications. As 
we move toward v1.0, we expect to remove these methods from ``BaseApp``.
