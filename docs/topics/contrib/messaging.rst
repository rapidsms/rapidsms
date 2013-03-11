==========================
rapidsms.contrib.messaging
==========================

.. module:: rapidsms.contrib.messaging

The `messaging` contrib application allows you to send messages to one or more
Contacts through a web interface.

.. _messaging-installation:

Installation
============

The `messaging` contrib application depends on `django-selectable
<http://django-selectable.readthedocs.org/>`_ to create a recipient
multi-selector with autocomplete on the front-end view. You can install
`django-selectable` using pip::

    pip install django-selectable

Next, you will need to add ``"rapidsms.contrib.messaging"`` and ``"selectable"``
(if not already present) to :setting:`INSTALLED_APPS` in your settings file::

    INSTALLED_APPS = [
        ...
        "rapidsms.contrib.messaging",
        "selectable",
        ...
    ]

Finally, you must add the URLs for `messaging` and `selectable` to your
urlconf::

    urlpatterns += ("",
        (r"^messaging/", include("rapidsms.contrib.messaging.urls")),
        (r"^selectable/", include("selectable.urls")),
    )

.. _messaging-usage:

Usage
=====

The messaging front-end view displays a form through which you can write a
text message and select its recipients. The recipient selector uses
autocomplete to search through all RapidSMS contacts. You may select any
number of recipients to receive the message.

When sending a message, the messaging application calls :func:`rapidsms.router.api.send`
with the message text and `recipient.default_connection` for each recipient.
If an error occurs, the message will not be sent to further recipients but it
may have already been sent to earlier recipients. The order in which messages
will be sent is not guaranteed.
