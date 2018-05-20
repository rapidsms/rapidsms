===========================
rapidsms.contrib.messagelog
===========================

.. module:: rapidsms.contrib.messagelog

The `messagelog` contrib application maintains a database record of all
messages sent and received by RapidSMS.

.. _messagelog-installation:

Installation
============

1. Add ``"rapidsms.contrib.messagelog"`` to :setting:`INSTALLED_APPS` in your
   settings file::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.messagelog",
        ...
    ]

2. Add `messagelog` URLs to your urlconf::

    urlpatterns = patterns("",
        ...
        (r"^messagelog/", include("rapidsms.contrib.messagelog.urls")),
        ...
    )

3. Create database tables for the `messagelog` models:

.. code-block:: bash

    $ python manage.py syncdb

4. Optionally, add a link to the message log view from your
   ``rapidsms/_nav_bar.html`` template:

.. code-block:: django

    {% load url from future %}
    <li><a href="{% url "message_log" %}">Message Log</a></li>

.. _messagelog-usage:

Usage
=====

`messagelog` defines the `Message` database model, which
stores key information about an `IncomingMessage` or `OutgoingMessage`:

    :connection: The RapidSMS `Connection` to which the message was sent.
    :contact: The RapidSMS `Contact` associated with the connection.
    :date: When the message was sent.
    :text: The text of the message.
    :direction: `Message.INCOMING` or `Message.OUTGOING`.

Upon :ref:`parsing an IncomingMessage <phase-parse>`, `messagelog`
creates a `Message` object and sets the `logger_msg` property of the
`IncomingMessage` to be the `Message` object.

Upon :ref:`processing an OutgoingMessage <phase-outgoing>`, `messagelog`
creates a `Message` object and sets the `logger_msg` property of the
`OutgoingMessage` to be the `Message` object.

You can navigate to the `message_log` view to browse the full list of stored
messages.
