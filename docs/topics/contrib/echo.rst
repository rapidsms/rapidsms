=====================
rapidsms.contrib.echo
=====================

.. module:: rapidsms.contrib.echo

The `echo` contrib application is a collection of two simple :doc:`handlers
</topics/contrib/handlers>` that can assist you in remotely debugging your
RapidSMS project.

.. _echo-installation:

Installation
============

To use either of `EchoHandler` or `PingHandler`, you must add
``"rapidsms.contrib.handlers"`` to
:setting:`INSTALLED_APPS` in your settings file::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.handlers",
        ...
    ]

Then add the handler classes you want to use to
:setting:`RAPIDSMS_HANDLERS`::

    RAPIDSMS_HANDLERS = [
        ...
        "rapidsms.contrib.echo.handlers.echo.EchoHandler",  # if you want EchoHandler
        "rapidsms.contrib.echo.handlers.ping.PingHandler",  # if you want PingHandler
        ...
    ]

See the :doc:`handlers docs </topics/contrib/handlers>` for more information
about how handlers are loaded and called.

.. _echo-usage:

Usage
=====

.. _echo-handler:

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

.. _ping-handler:

PingHandler
-----------

`PingHandler` is an extension of :ref:`BaseHandler <base-handler>`. It handles
messages with the (precise) text "ping" by responding with "pong". Unlike
many handlers, this one is case-sensitive and does not allow extra whitespace.
This handler is useful for remotely checking that the router is alive.

For example::

    > ping
    < pong
