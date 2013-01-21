=========================
rapidsms.contrib.handlers
=========================

.. module:: rapidsms.contrib.handlers

The `handler` contrib app provides three classes- `BaseHandler`,
`KeywordHandler`, and `PatternHandler`- which can be extended to help you
create RapidSMS applications quickly.

.. _handler-installation:

Installation
============

To define and use handlers for your RapidSMS project, you will need to
add `rapidsms.contrib.handlers` to :setting:`INSTALLED_APPS` in your settings
file. This application will load handlers according to the configuration
parameters defined in your settings, as described in :ref:`handler discovery
<handler-discovery>`.

.. _handler-usage:

Usage
=====

.. _keyword-handler:

KeywordHandler
--------------

Many RapidSMS applications operate based on whether a message begins with a
specific keyword. By subclassing `KeywordHandler`, you can easily create a
simple, keyword-based application::

    from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

    class LatrineHandler(KeywordHandler):
        keyword = "latrine"

        def help(self):
            self.respond("Send LATRINE FULL or LATRINE EMPTY.")

        def handle(self, text):
            if text.upper() == "FULL":
                self.respond("Please empty the latrine.")

            elif text.upper() == "EMPTY":
                self.respond("That's great news.")

            else:
                self.help()

Your handler must define three things: `keyword`, `help()`, and `handle(text)`.
When a message is received that begins with the keyword (case insensitive),
the remaining text is passed to the `handle` method of the class. If no
additional non-whitespace text is included with the message, `help` is called
instead. For example::

    > latrine
    < Send LATRINE FULL or LATRINE EMPTY.
    > latrine full
    < Please empty the latrine.
    > latrine empty
    < That's great news.
    > latrine something else
    < Send LATRINE FULL or LATRINE EMPTY.

All non-matching messages are silently ignored to allow other applications and
handlers to catch them.

.. _pattern-handler:

PatternHandler
--------------

.. NOTE::
   Pattern-based handlers are not usually a good idea - it is cumbersome to
   write patterns with enough flexibility to be used in the real world.
   However, it is very handy for prototyping, and can be easily upgraded later.

The `handlers` contrib app also provides a `PatternHandler` class, which can
be subclassed to create applications which respond to a message based on
whether a specific pattern is matched::

    from rapidsms.contrib.handlers.handlers.pattern import PatternHandler

    class SumHandler(PatternHandler):
        pattern = r"^(\d+) plus (\d+)$"

        def handle(self, a, b):
            a, b = int(a), int(b)
            total = a + b
            self.respond("%d + %d = %d" % (a, b, total))

Your handler must define `pattern` and `handle(*args)`. The pattern is
case-insensitive, but must otherwise be precisely matched (for example, no
trailing whitespace). When the pattern is matched, the `handle` method is
called with the captures as arguments. As an example, the above application
could create the following conversation::

    > 1 plus 2
    < 1 + 2 = 3

Like the `KeywordHandler`, the `PatternHandler` silently ignores all
non-matching messages to allow other apps and handlers to catch them.

BaseHandler
-----------

All handlers, including the `KeywordHandler` and `PatternHandler`, are derived
from the `BaseHandler` class. All instances of `BaseHandler` have access to
`self.msg` and `self.router`, as well as the methods `self.respond` and
`self.respond_error` (which respond to the instance's message). They also can
use the `test` method, which creates a simple environment for testing a
handler's response to a specific message::

    >>> from rapidsms.contrib.handlers.handlers.base import BaseHandler
    >>> class AlwaysHandler(BaseHandler):
    ...
    ...    @classmethod
    ...    def dispatch(cls, router, msg):
    ...        msg.respond("xxx")
    ...        msg.respond("yyy")
    ...        return True

    >>> AlwaysHandler.test('anything')
    ['xxx', 'yyy']

.. IMPORTANT::
   It is important to note that the first handler to accept the message will
   block all others. The order in which the handlers are called is not
   guaranteed, so each handler should be as conservative as possible when
   choosing to respond to a message.

.. _handler-discovery:

Handler Discovery
=================

Handlers may be defined in the `handlers` subdirectory of any Django app
listed in :setting:`INSTALLED_APPS`. Each file in the `handlers` subdirectory
is expected to contain exactly one new-style Python class which extends from
one of the core handler classes.

Handler discovery, which occurs when the `handlers` application is loaded, can
be configured using the following project settings:

- :setting:`RAPIDSMS_HANDLERS_EXCLUDE_APPS` - The application will not load
  handlers from any Django app included in this list.

- :setting:`INSTALLED_HANDLERS` - If this list is not `None`, the application
  will load only handlers that are included in this list.

- :setting:`EXCLUDED_HANDLERS` - The application will not load any handler
  that is included in this list.

.. NOTE::
   Prefix matching is used to determine which handlers are described in
   :setting:`INSTALLED_HANDLERS` and :setting:`EXCLUDED_HANDLERS`. The module
   name of each handler is compared to each value in these settings to see if
   it *starts with* the value.
