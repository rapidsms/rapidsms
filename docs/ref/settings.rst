========
Settings
========

Here is a full list of available settings, and their default values, for
RapidSMS and its contrib apps.

.. setting:: DEFAULT_RESPONSE

DEFAULT_RESPONSE
----------------

:App: :doc:`rapidsms.contrib.default </topics/contrib/default>`
:Default: ``'Sorry, %(project_name)s coud not understand your message.'``

The default response to an `IncomingMessage` that is not handled by any other
application. To include :setting:`PROJECT_NAME`, use ``'%(project_name)s'`` in
the string.

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
            'ENGINE': 'path.to.backend1',
        },
        'backend2_name': {
            'ENGINE': 'path.to.backend2',
        },
    }

Each backend dictionary requires only the 'ENGINE' key, which defines the
Python path to the backend. Other key-value pairs can be used to configure
backend-specific options.

Example configuration::

    INSTALLED_BACKENDS = {
        "message_tester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
    }

.. setting:: PROJECT_NAME

PROJECT_NAME
------------

:Default: ``'RapidSMS'``

The name of your project. This is used by some apps such as
:doc:`rapidsms.contrib.default </topics/contrib/default>` to customize message
responses.

.. setting:: RAPIDSMS_ROUTER

RAPIDSMS_ROUTER
---------------

.. versionadded:: 0.10.0

:Default: ``'rapidsms.router.blocking.BlockingRouter'``

The router is used to handle incoming and outgoing messages. For the list of
available routers see :doc:`/topics/router/index`.
