.. module:: rapidsms.router.db
.. router:: DatabaseRouter

DatabaseRouter
==============

:router:`DatabaseRouter` provides the following functionality:

* All inbound and outbound messages are stored in the database.
* Inbound messages are processed asynchronously with Celery_.
* Outbound messages are automatically split into batches for asynchronous sending.
* Use of Django's `bulk create`_ to optimize database inserts.
* Messages that fail to send will use `Celery's retry`_ mechanism.

Similar to :router:`CeleryRouter`, :router:`DatabaseRouter` is designed for
projects that require high messages volumes.

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
        "rapidsms.router.db"
    )

This will register Celery tasks in ``rapidsms.router.db.tasks``.

Set :setting:`RAPIDSMS_ROUTER` to use :router:`CeleryRouter`::

    RAPIDSMS_ROUTER = "rapidsms.router.db.DatabaseRouter"

Run ``syncdb`` to create the necessary database tables::

    python manage.py syncdb

That's it!

.. _django-celery: http://pypi.python.org/pypi/django-celery
.. _setup instructions: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
.. _calling tasks: http://docs.celeryproject.org/en/latest/userguide/calling.html
.. _Celery: http://www.celeryproject.org/
.. _Django logging documentation: https://docs.djangoproject.com/en/dev/topics/logging/
.. _bulk create: https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create
.. _Celery's retry: http://docs.celeryproject.org/en/latest/userguide/tasks.html#retrying
