.. _logging:

Logging
*******

It's good practice to log a message using Python logging
whenever an error or exception occurs.  There are a myriad
of tools administrators can then use to send the information
where they want it, send email alerts, analyze trends, etc.

If you want to log in your app, just::

    import logging
    logger = logging.getLogger(__name__)

and use::

    logger.debug("msg")
    logger.critical("msg")
    logger.exception("msg")
    # etc.

All RapidSMS core logging can now be captured using the ``'rapidsms'``
root logger.  (There's not a lot of logging from the core yet, but pull
requests are welcome.)

For example, if you wanted messages from the RapidSMS
core to be written to a file `"/path/rapidsms.log"`, you could define
a new handler in the :setting:`LOGGING` setting in Django:

.. code-block:: python
    :emphasize-lines: 5-9

    LOGGING = {
        ...
        'handlers': {
            ...
            'rapidsms_file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/path/rapidsms.log',
            },
            ...
        },
        ...
    }

Setting ``level`` to ``DEBUG`` means all messages of level DEBUG and
lower will be passed through (that's all of them). Then this handler
will write those messages to the file ``/path/rapidsms.log``.  They'll
be formatted by the default formatter.

Then configure the ``rapidsms`` logger to send messages to that handler:

.. code-block:: python
    :emphasize-lines: 4-8

    LOGGING = {
        ...
        'loggers': {
            'rapidsms': {
                'handlers': ['rapidsms_file'],
                'propagate': True,
                'level': 'DEBUG',
            },
        },
        ...
    }

Setting ``level`` to ``DEBUG`` means all messages of level DEBUG and
lower will be passed through (that's all of them).

The logger name ``rapidsms`` means any logger to a name that matches
that (``rapidsms``, ``rapidsms.models``, etc) will be passed to this
handler to handle.

Setting ``propagate`` to ``True`` means the same messages will be
passed to other handlers if they also match. (This handler does not
consume the messages.)

If you created your project with the latest
:ref:`Rapidsms project template <rapidsms-project-template>`
and haven't changed the settings, all rapidsms logging will be written
to `rapidsms.log` in your project directory.
