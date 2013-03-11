===========================
rapidsms.contrib.httptester
===========================

.. module:: rapidsms.contrib.httptester

The `httptester` contrib application allows sending fake messages to RapidSMS
and seeing how RapidSMS responds.

.. _httptester-installation:

Installation
============

To define and use Message Tester for your RapidSMS project, you will need to:

1. Add ``"rapidsms.contrib.httptester"`` to :setting:`INSTALLED_APPS` in your
   settings file::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.httptester",
        ...
    ]

1. Add `httptester` URLs to your urlconf somewhere, for example::

    urlpatterns = patterns("",
        ...
        (r"^httptester/", include("rapidsms.contrib.httptester.urls")),
        ...
    )

1. Add the Message Tester backend to :setting:`INSTALLED_BACKENDS`::

    INSTALLED_BACKENDS = {
        ...
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
        ...
    }

1. Create database tables for the `httptester` models:

.. code-block:: bash

    $ python manage.py syncdb

1. Add the Message Tester view to the RapidSMS tabs::

    RAPIDSMS_TABS = [
        ...
        ("rapidsms.contrib.httptester.views.generate_identity", "Message Tester"),
        ...
    ]

.. _httptester-usage:

Usage
=====

With Message Tester installed, there will be a `Message Tester` tab
in the RapidSMS web page header. Click on that tab to bring up
Message Tester.

Most of the controls for the Message Tester are in the left-side
column.

The phone number field contains the phone number which will be used
as the source number when you send test messages. A random number will
have been filled in for you, but you can change it to anything you want.

You can send a single message by typing the message in the `Single
Message` field and clicking `Send`.  Or you can send multiple messages
by putting each message on one line of a text file, selecting that
text file with the `Choose File` button, and clicking `Send`.

The Log table on the right side of the page will show messages you send, and any
messages that RapidSMS replies with.  For messages that you send,
the left column will show the phone number the message came from, and
a double arrow pointing right, with the text of the message in the right
column. For messages that RapidSMS sends, the left column will show the
phone number the message was sent to, and a double arrow pointing left,
with the text of the message again in the right column.

The Log table will always show the most recent messages. If there are
more than will fit on a page, you can use the paging controls at the
bottom of the table to page back through the messages.

You can clear the log of messages for the current phone number by selecting
the `Clear` checkbox and clicking `Send`, or the entire log by selecting
the `Clear all` checkbox and clicking `Send`.
