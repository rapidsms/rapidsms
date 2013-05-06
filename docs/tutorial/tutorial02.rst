.. _tutorial02:

RapidSMS Tutorial Part 2
========================

*This tutorial is a draft.* Comments are welcome in `this discussion`_ on Google Groups.

.. _this discussion: https://groups.google.com/forum/#!topic/rapidsms-dev/NLd3lUinUFQ


We'll continue the tutorial by introducing the RapidSMS default app.
Then we'll show how using RapidSMS handlers can handle parsing
incoming messages for you.

Default Application
-------------------

In :ref:`part 1 <tutorial01>`, we saw the :ref:`default application <default-app>`
doing its work, responding to messages that no other application had handled.
It's a good idea to keep the default application at the end of
:setting:`INSTALLED_APPS` so that it can give some response when your
application doesn't recognize a message. Otherwise your users will get
no response and won't know there was a problem. Or worse, the default application
will respond to the message before your app sees it, confusing the user.

You can change the response used by the default application by changing
:setting:`DEFAULT_RESPONSE`. For example, if you've implemented a HELP
command in your project, you might change the default response to:

.. code-block:: python

    DEFAULT_RESPONSE = "Sorry, %(project_name)s could not \
    understand your message.  Send HELP to get a list of \
    valid commands."

Of course, you could also just send the help in the default response.

"Handling" a Message
~~~~~~~~~~~~~~~~~~~~

We said the default application would respond if no other application had
handled the message, but how does RapidSMS know that an application has
"handled" the message?

One way is for an application's :ref:`handle <phase-handle>` method to
return ``True``.
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

There are a few very common cases for RapidSMS, such as looking for
messages starting with a particular word, or messages that match a
particular pattern. Instead of writing that code over and over yourself,
you can use RapidSMS handlers.

Using handlers has three steps:

1. Write one or more subclasses of handler classes.
2. Add `"rapidsms.contrib.handlers"` to :setting:`INSTALLED_APPS`.
3. Add the full classnames of each of your new classes to :setting:`RAPIDSMS_HANDLERS`.


Keyword Handlers
~~~~~~~~~~~~~~~~

We mentioned earlier that you might want to implement a HELP command for
your users. We can do that using a :ref:`Keyword Handler <keyword-handler>`.

You'll write a class that subclasses
:py:class:`~rapidsms.contrib.handlers.KeywordHandler`. Your keyword will
be "help" (it's not case sensitive).  If someone sends just "HELP", we'll
respond with a message telling them how to get more help. If someone
sends "HELP something", we'll give them more specific help if we can,
and otherwise send the same response we would to a bare "HELP".

.. code-block:: python

    # mypackage/help.py

    from rapidsms.contrib.handlers import KeywordHandler

    from somewhere import help


    class HelpHandler(KeywordHandler):
        keyword = "help"

        def help(self):
            """Invoked if someone just sends `HELP`.  We also call this
            from `handle` if we don't recognize the arguments to HELP.
            """
            self.respond("Allowed commands are AAA, BBB, and CCC. Send "
                         "HELP <command> for more help on a specific command.")

        def handle(self, text):
            """Invoked if someone sends `HELP <any text>`"""
            text = text.strip().lower()
            if text == 'aaa':
                self.respond(help['aaa'])
            elif text == 'bbb':
                self.respond(help['bbb])
            elif text == 'ccc':
                self.respond(help['ccc'])
            else:
                self.help()

Now, add `"rapidsms.contrib.handlers"` to :setting:`INSTALLED_APPS`::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.handlers",
        ...
    ]

and add your new class to :setting:`RAPIDSMS_HANDLERS`::

    RAPIDSMS_HANDLERS = [
        ...
        "mypackage.help.HelpHandler",
        ...
    ]

Now, if you start RapidSMS and send a message "HELP", you should get
this response::

    Allowed commands are AAA, BBB, and CCC. Send HELP <command> for more help on a specific command.

and if you send "HELP AAA", you should get whatever help is available for AAA.

Handlers Must Handle
~~~~~~~~~~~~~~~~~~~~

We need to issue a warning here - when a handler is called for a message,
the handler must handle the message itself, because no other handlers or apps
will be called. Since this handler matched the message, RapidSMS expects
that this handler will take care of the message. If you need more flexibility,
you'll need to write a normal RapidSMS application.

Pattern Handlers
~~~~~~~~~~~~~~~~

A :ref:`Pattern Handler <pattern-handler>` is like a keyword handler, but
with two differences:

1. The pattern can match any part of the message, not just the beginning
2. Groups can be used in the regular expression to help parse the message. Whatever matches the groups is passed to your handler.

Be careful when deciding to use a pattern handler. Your
regular expression needs to be flexible enough to cope with any message
someone might send that you want your handler to handle.

Here's an example from the :py:class:`~rapidsms.contrib.handlers.PatternHandler`
documentation.  You can send a message like "5 plus 3" and it will respond
"5+3 = 8". Note that you cannot send "5 + 3" or "5plus3" or "5 plus 3 ";
none of those match this simple regular expression, so this handler won't
be invoked::

    >>> class SumHandler(PatternHandler):
    ...    pattern = r'^(\d+) plus (\d+)$'
    ...
    ...    def handle(self, a, b):
    ...        a, b = int(a), int(b)
    ...        total = a + b
    ...
    ...        self.respond(
    ...            "%d+%d = %d" %
    ...            (a, b, total))

    >>> SumHandler.test("1 plus 2")
    ['1+2 = 3']

Continue with :ref:`tutorial03`.
