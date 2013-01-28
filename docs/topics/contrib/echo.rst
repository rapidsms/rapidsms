rapidsms.contrib.echo
=====================

.. module:: rapidsms.contrib.echo

The `echo` contrib app is a collection of two simple :doc:`handlers
</topics/contrib/handlers>` that can assist you in remotely debugging your
RapidSMS project.

Installation
============

To use either of the echo or ping handlers, you must add both
"rapidsms.contrib.handlers" and "rapidsms.contrib.echo" to
:setting:`INSTALLED_APPS` in your settings file. See the :doc:`handlers docs
</topics/contrib/handlers>` for more information about how handlers are loaded
and called.

Usage
=====

EchoHandler
-----------

`EchoHandler` is an extension of :ref:`KeywordHandler <keyword-handler>` which
handles any message prefixed by "echo" by responding with the remainder of the
text. This handler is useful for remotely testing internationalization.

For example::

    > echo
    < To echo some text, send: ECHO <ANYTHING>
    > echo hello
    < hello

PingHandler
-----------

`PingHandler` is an extension of :ref:`BaseHandler <base-handler>` which
handles messages with the (precise) text "ping" by responding with "pong".
This handler is useful for remotely checking that the router is alive.

For example::

    > ping
    < pong
