Usage
=====

The `default` app allows your project to define a default response to an
`IncomingMessage` that is not handled by any other app. The response string
is defined in :setting:`DEFAULT_RESPONSE`.

This app operates during the :ref:`default message processing stage
<phase-default>`. It is very important that the router loads this app last,
both because all other apps should have the opportunity to handle the message
before falling back to this app, and because this app does not prevent the
execution of default stages of the apps that come after it.

The app passes the value of :setting:`PROJECT_NAME` to the response string. To
include the project name, use ``%(project_name)s`` in the response string.

If :setting:`DEFAULT_RESPONSE` is `None`, the `default` app will not send a
message.

By default, :setting:`DEFAULT_RESPONSE` is defined as::

    DEFAULT_RESPONSE = "Sorry, %(project_name)s could not understand your message."

Installation
============

To use the `default` app, simply add 'rapidsms.contrib.default' to the end of
:setting:`INSTALLED_APPS` in your settings file. The :doc:`BlockingRouter
</topics/router/router>` automatically loads the RapidSMS apps defined in
:setting:`INSTALLED_APPS`.
