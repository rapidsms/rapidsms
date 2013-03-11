========================
rapidsms.contrib.default
========================

.. module:: rapidsms.contrib.default

The `default` application allows your project to define a default response to
an `IncomingMessage` that is not handled by any other application. The
response string is defined in :setting:`DEFAULT_RESPONSE`.

.. _default-installation:

Installation
============

To use the `default` application, add ``"rapidsms.contrib.default"`` to the end
of :setting:`INSTALLED_APPS` in your settings file::

    INSTALLED_APPS = [
        # Your other installed apps
        ...
        "rapidsms.contrib.default"  # must be last
    ]

.. _default-usage:

Usage
=====

This application operates during the :ref:`default message processing stage
<phase-default>`. It is very important that the router loads this application
last, both because all other applications should have the opportunity to
handle the message before falling back to this one, and because this
application does not prevent the execution of default stages of the
applications that come after it.

The application passes the value of :setting:`PROJECT_NAME` to the response
string. To include the project name, use ``%(project_name)s`` in the response
string.

If :setting:`DEFAULT_RESPONSE` is `None`, the `default` application will not
send a message.

By default, :setting:`DEFAULT_RESPONSE` is defined as::

    DEFAULT_RESPONSE = "Sorry, %(project_name)s could not understand your message."


