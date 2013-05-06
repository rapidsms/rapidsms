.. _tutorial02:

RapidSMS Tutorial Part 2
========================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ


We'll continue the tutorial by introducing the RapidSMS default app,
and converting our minimal application from part 1 into a
RapidSMS handler. We'll look at how keyword and pattern handlers
can help build simple RapidSMS applications quickly.

Default Application
-------------------

In :ref:`part 1 <tutorial01>`, we saw the :ref:`default application <default-app>`
doing its work, responding to messages that no other application had handled.
It's a good idea to keep the default application at the end of
:setting:`INSTALLED_APPS` so that it can give some response when your
application doesn't recognize a message. Otherwise your users will get
no response and won't know there was a problem.

You can change the response used by the default application by changing
:setting:`DEFAULT_RESPONSE`. For example, if you've implemented a HELP
command in your project, you might change the default response to:

.. code-block:: python

    DEFAULT_RESPONSE = ""Sorry, %(project_name)s could not \
    understand your message.  Send HELP to get a list of \
    valid commands."

"Handling" a Message
~~~~~~~~~~~~~~~~~~~~

We said the default application would respond if no other application had
handled the message, but how does RapidSMS know that an application has
"handled" the message?

One way is for an application's :ref:`handle <phase-handle>` method to return ``True``.
That tells RapidSMS that the application has handled the message and no
other applications need to try to handle it too. On the other hand,
if the application returns ``False``, RapidSMS will continue passing
the message to applications in its list until one returns ``True`` or
it runs out of applications.

That's why the default application should
be kept at the end of the :setting:`INSTALLED_APPS`, because we don't
want RapidSMS to call the default application until it has tried every
other one, and RapidSMS calls the applications in the order of
:setting:`INSTALLED_APPS`.


RapidSMS Handlers
-----------------



Keyword Handlers
~~~~~~~~~~~~~~~~

Pattern Handlers
~~~~~~~~~~~~~~~~


Continue with :ref:`tutorial03`.
