========
Settings
========

Here's a full list of all available settings, in alphabetical order, and their
default values.

.. setting:: RAPIDSMS_ROUTER

RAPIDSMS_ROUTER
----------------------

.. versionadded:: 0.10.0

Default: ``'rapidsms.router.blocking.BlockingRouter'``

The router is used to handle incoming and outgoing messages. For the list of
available routers see :doc:`/topics/router`.


.. setting:: INSTALLED_BACKENDS

INSTALLED_BACKENDS
------------------
INSTALLED_BACKENDS is a dictionary that defines the list of backends to use. This setting is not provided in the default installation as individual project needs vary. This setting mimics the structure of the Django DATABASES setting, and has the following
general format::

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
    }

Each value in INSTALLED_BACKENDS is a dictionary of the format::

    "backend_name": {
        "ENGINE": "path.to.backend",
    }

"ENGINE" is the only required key of this dictionary, and defines the python path to the backend to use. Other key value pairs can be used to configure options specific to each backend.
