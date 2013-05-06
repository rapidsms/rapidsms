========
Settings
========

Here is a full list of available settings, and their default values, for
RapidSMS and its contrib apps.

.. setting:: DB_ROUTER_DEFAULT_BATCH_SIZE

DB_ROUTER_DEFAULT_BATCH_SIZE
----------------------------

:App: :doc:`rapidsms.router.db </topics/router/db>`
:Default: 200

The default maximum batch size when the database router is sending messages
in bulk.

.. setting:: DEFAULT_RESPONSE

DEFAULT_RESPONSE
----------------

:App: :doc:`rapidsms.contrib.default </topics/contrib/default>`
:Default: ``'Sorry, %(project_name)s could not understand your message.'``

The default response to an `IncomingMessage` that is not handled by any other
application. To include :setting:`PROJECT_NAME`, use ``'%(project_name)s'`` in
the string.

.. setting:: EXCLUDED_HANDLERS

EXCLUDED_HANDLERS
-----------------

:App: :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>`
:Default: ``[]``

.. deprecated:: 0.15.0
    See :setting:`RAPIDSMS_HANDLERS` instead.

The :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>` application
will not load any handler in a module that is in this list. The module name of
each handler is compared to the value in this list using prefix matching. For
more information, see :ref:`handlers-discovery`.

.. setting:: INSTALLED_BACKENDS

INSTALLED_BACKENDS
------------------

:Default: *not set*

This setting is a dictionary that allows you to configure backends for use
in your project. There is no default value as the needs of individual projects
vary widely. This setting mimics the structure of the Django
:setting:`DATABASES` setting, with the following general format::

    INSTALLED_BACKENDS = {
        'backend1_name': {
            'ENGINE': 'path.to.backend1.BackendClass',
        },
        'backend2_name': {
            'ENGINE': 'path.to.backend2.BackendClass',
        },
    }

Each backend dictionary requires only the 'ENGINE' key, which defines the
Python path to the backend. Other key-value pairs can be used to configure
backend-specific options.

Example configuration::

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend.HttpTesterCacheBackend",
        },
    }

.. setting:: INSTALLED_HANDLERS

INSTALLED_HANDLERS
------------------

:App: :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>`
:Default: ``None``

.. deprecated:: 0.15.0
    See :setting:`RAPIDSMS_HANDLERS` instead.

If this setting is not ``None``, the :doc:`rapidsms.contrib.handlers
</topics/contrib/handlers>` application will only load handlers in modules
that are in this list. The module name of each handler is compared to each
value in this list using prefix matching. For more information see
:ref:`handlers-discovery`.

.. setting:: PROJECT_NAME

PROJECT_NAME
------------

:Default: ``'RapidSMS'``

The name of your project. This is used by some applications such as
:doc:`rapidsms.contrib.default </topics/contrib/default>` to customize message
responses.

.. setting:: RAPIDSMS_HANDLERS

RAPIDSMS_HANDLERS
-----------------

.. versionadded:: 0.15.0

:App: :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>`
:Default: ``[]``

A list of names of the handler classes that should be loaded. For more
information see :ref:`handlers-discovery`.

If this is set, it overrides the older, deprecated behavior of loading
all handlers, modified by :setting:`INSTALLED_HANDLERS`,
:setting:`EXCLUDED_HANDLERS`,
and :setting:`RAPIDSMS_HANDLERS_EXCLUDE_APPS`.

.. setting:: RAPIDSMS_HANDLERS_EXCLUDE_APPS

RAPIDSMS_HANDLERS_EXCLUDE_APPS
------------------------------

:App: :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>`
:Default: ``[]``

.. deprecated:: 0.15.0
    See :setting:`RAPIDSMS_HANDLERS` instead.

The :doc:`rapidsms.contrib.handlers </topics/contrib/handlers>` application
will not load handlers from any Django app included in this list. For more
information see :ref:`handlers-discovery`.

.. setting:: RAPIDSMS_ROUTER

RAPIDSMS_ROUTER
---------------

.. versionadded:: 0.10.0

:Default: ``'rapidsms.router.blocking.BlockingRouter'``

The router is used to handle incoming and outgoing messages. For the list of
available routers see :doc:`/topics/router/index`.
