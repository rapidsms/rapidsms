.. module:: rapidsms.router.db
.. router:: DatabaseRouter

DatabaseRouter
==============

.. versionadded:: 0.13.0

:router:`DatabaseRouter` provides the following functionality:

* All inbound and outbound messages are stored in the database.
* Inbound and outbound messages are processed asynchronously with Celery_.
* Outbound messages are automatically split into batches for sending.
* Use of Django's `bulk create`_ to optimize database inserts.
* Messages that fail to send will use `Celery's retry`_ mechanism.

Similar to :router:`CeleryRouter`, :router:`DatabaseRouter` is designed for
projects that require high messages volumes.

How it works
------------

* Before doing any processing, an inbound message is loaded into the ``Message`` and ``Transmission`` models. A celery task is then queued to process the message asynchronously.
* The celery task reconstructs the message object, fires up the router, and passes it off for inbound processing.
* Any replies are loaded into the ``Message`` and ``Transmission`` models.
* The router then divides the outbound messages by backend and queues tasks for sending chunks of messages to their respective backends.
* As tasks complete, the status of the messages are updated in the database, including any errors that occurred.

Installation
------------

.. note::

    :router:`DatabaseRouter` depends on `django-celery`_ 3.0+. Please follow
    the django-celery `setup instructions`_ before proceeding.

Add ``rapidsms.router.db`` to ``INSTALLED_APPS``:

.. code-block:: python
   :emphasize-lines: 3

    INSTALLED_APPS = (
        # Other apps here
        "rapidsms.router.db",
    )

This will register Celery tasks in ``rapidsms.router.db.tasks``.

Set :setting:`RAPIDSMS_ROUTER` to use :router:`DatabaseRouter`::

    RAPIDSMS_ROUTER = "rapidsms.router.db.DatabaseRouter"

Run ``syncdb`` to create the necessary database tables::

    python manage.py syncdb

That's it!

Configuration
-------------

The database router has one optional setting,
:setting:`DB_ROUTER_DEFAULT_BATCH_SIZE`, to change the default
maximum size of a batch of messages from 200.

Celery workers
**************

Finally, you'll need to run the celery worker command (in a separate shell from
``runserver``) to begin consuming queued tasks::

    python manage.py celery worker --loglevel=info

Now your messages will be handled asynchronously with :router:`DatabaseRouter`.

.. module:: rapidsms.router.db.models

Database models
---------------

:router:`DatabaseRouter` utilizes two database models, ``Message`` and
``Transmission``.

Message
*******

The ``Message`` model contains the context of a text message. For every associated ``Connection``, a ``Message`` has an associated ``Transmission``.

.. class:: Message

    .. attribute:: direction

        Required. Either ``'I'`` or ``'O'``.

    .. attribute:: status

        Required. See :ref:`message-status-values`.

    .. attribute:: date

        Required. Date/time when message was created.

    .. attribute:: updated

        Required. Last date/time the message was updated.

    .. attribute:: sent

        Date/time when all associated transmissions were sent.

    .. attribute:: delivered

        Date/time when all associated transmissions were delivered (requires backend functionality).

    .. attribute:: text

        Required. Message text.

    .. attribute:: external_id

        Optional. ID of message as defined by the associated backend.

    .. attribute:: in_response_to

        Optional. Foreign key to ``Message`` that generated this reply.

Transmission
************

A ``Transmission`` represents the instance of a particular ``Message`` and ``Connection``.

.. class:: Transmission

    .. attribute:: message

        Required. Foreign key to associated ``Message``.

    .. attribute:: connection

        Required. Foreign key to associated ``Connection``.

    .. attribute:: status

        Required. See :ref:`message-status-values`.

    .. attribute:: date

        Required. Date/time when transmission was created.

    .. attribute:: updated

        Required. Last date/time when transmission was updated.

    .. attribute:: sent

        Date/time when transmission was sent.

    .. attribute:: delivered

        Date/time when transmission was delivered (requires backend functionality).

.. _message-status-values:

Message status values
*********************

``Message`` and ``Transmission`` objects can have the following status values:

* Inbound values:
    * ``Q`` - *Queued*: Message is queued and awaiting processing
    * ``R`` - *Received*: Message has been processed and responses are queued
    * ``E`` - *Errored*: An error occurred during processing
* Outbound values:
    * ``Q`` - *Queued*: Message is queued and awaiting processing
    * ``P`` - *Processing*: Message is sending
    * ``S`` - *Sent*: All associated transmissions have been sent
    * ``D`` - *Delivered*: All associated transmissions have been delivered (requires backend functionality)
    * ``E`` - *Errored*: An error occurred during processing

.. _django-celery: http://pypi.python.org/pypi/django-celery
.. _setup instructions: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
.. _calling tasks: http://docs.celeryproject.org/en/latest/userguide/calling.html
.. _Celery: http://www.celeryproject.org/
.. _Django logging documentation: https://docs.djangoproject.com/en/dev/topics/logging/
.. _bulk create: https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
.. _Celery's retry: http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying
