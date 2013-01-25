.. module:: rapidsms.router.celery
.. router:: CeleryRouter

CeleryRouter
============

:router:`CeleryRouter` uses Celery_ to queue incoming and outgoing messages.

:router:`BlockingRouter` processes messages synchronously in the main HTTP
thread. This is fine for most scenarios, but in some cases you may wish to
process messages outside of the HTTP request/response cycle to be more
efficient. :router:`CeleryRouter` is a custom router that allows you queue
messages for background processing. It's designed for projects that require
high messages volumes and greater concurrency.

Installation
------------

.. note::

    :router:`CeleryRouter` depends on `django-celery`_ 3.0+. Please follow
    the setup instructions in
    :doc:`Scheduling Tasks with Celery <../celery>` before proceeding.

Add ``rapidsms.router.celery`` to ``INSTALLED_APPS``:

.. code-block:: python
   :emphasize-lines: 3

    INSTALLED_APPS = (
        # Other apps here
        "rapidsms.router.celery"
    )

This will register Celery tasks in ``rapidsms.router.celery.tasks``.

Set :setting:`RAPIDSMS_ROUTER` to use :router:`CeleryRouter`::

    RAPIDSMS_ROUTER = "rapidsms.router.celery.CeleryRouter"

That's it! Now all incoming and outgoing messages will be queued using Celery.

Configuration
-------------

Eager backends
~~~~~~~~~~~~~~

Sometimes your project may require the use of a synchronous backend. If this is
the case, you can configure specific backends to utilize Celery's eager
functionality with the ``router.celery.eager`` backend setting. For example,
here's how you can force the httptester backend to be eager:

.. code-block:: python
   :emphasize-lines: 4

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
            "router.celery.eager": True,
        },
    }

Using this setting means that the task will be executed in the current process,
and not by an asynchronous worker. Please see the Celery documentation for more
information on `calling tasks`_.

Logging
~~~~~~~

.. note::

    Please see the `Django logging documentation`_ for further information
    regarding general logging configuration.

All logging specific to :router:`CeleryRouter` is handled through the
``rapidsms.router.celery`` name. For example, if you have a ``file`` handler defined, you can capture all messages using the following configuration::

    LOGGING_CONFIG = {
        'rapidsms.router.celery': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }

Currently, there are only two child loggers: one for the router and one for the
Celery task. You can capture their messages independently like so::

    LOGGING_CONFIG = {
        'rapidsms.router.celery.router': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'rapidsms.router.celery.tasks.rapidsms_handle_message': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }

BlockingRouter
**************

:router:`CeleryRouter` uses :router:`BlockingRouter` to route
messages. If you want to capture all router messages, make sure to add, in
addition to the :router:`CeleryRouter` loggers, ``blockingrouter``::

    LOGGING_CONFIG = {
        'blockingrouter': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }

.. _django-celery: http://pypi.python.org/pypi/django-celery
.. _setup instructions: http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
.. _calling tasks: http://docs.celeryproject.org/en/latest/userguide/calling.html
.. _Celery: http://www.celeryproject.org/
.. _Django logging documentation: https://docs.djangoproject.com/en/dev/topics/logging/
