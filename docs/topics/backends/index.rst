.. _rapidsms-backends:

RapidSMS Backends
=================

.. module:: rapidsms.backends

Overview
--------

Backends define how RapidSMS communicates with the outside world. The router
uses backends to send and receive messages and all text messages will
eventually pass through a backend. They handle a two-way messaging protocol:

* **Incoming messages:** Messages received by RapidSMS from an external source. All incoming messages are received over HTTP and processed by a Django view. Once received, backends will pass messages to the router for processing.
* **Outgoing messages:** Messages sent by RapidSMS to an external source. The router will pass messages to backends once processed. RapidSMS sends messages over HTTP.

.. _supplied-backends:

Supplied Backends
-----------------

RapidSMS includes several backends in core for you to use:

* :ref:`Kannel backend <kannel_configuration>`
* :ref:`Vumi backend <vumi_configuration>`
* :ref:`HTTP backend <http-backend>`

However, many other backends exist in the RapidSMS community and can be
installed for use in your own project. If you can't find a backend that's
suitable for your needs, you can write a :ref:`custom backend 
<custom-backends>`.


Configuration
-------------

The instructions below describe how backend configuration works in the general
sense. Backends will provide their own installation instructions. If you want
to install a specific backend, please follow the backend-specific
documentation.

All backends will require the following basic configuration:


.. _backend-settings:

``INSTALLED_BACKENDS``
**********************

First, you'll need to add your backend to :setting:`INSTALLED_BACKENDS`. This
setting is a key/value pairing of **backend name** to a configuration
dictionary. For example::

    INSTALLED_BACKENDS = {
        "my-backend1": {
            "ENGINE": "path.to.BackendClass",
            "example-configuration-option": "Yes",
        },
        "my-backend2": {
            "ENGINE": "path.to.OtherBackendClass",
            "use-special-method": True,
        },
    }

This examples defines two backends named ``my-backend1`` and ``my-backend2``.
The **backend name** can be anything, but it will be used by the router and for
matching up with :ref:`Backend URLs <backend-urls>`. The only required
configuration option is ``ENGINE``, which is the dotted Python path to the
backend class. Additional configuration can be supplied to backends.


.. _backend-urls:

URLs
****

Backends communicate over HTTP and Django uses views to process HTTP requests,
so all backends require a Django URL endpoint and view to handle incoming
messages. For example::

    from django.conf.urls import patterns, url
    from path.to.backend1 import ExampleBackendView
    from path.to.backend2 import OtherBackendView

    urlpatterns = patterns('',
        url(r"^backend/my-backend1/$",
            ExampleBackendView.as_view(backend_name="my-backend1")),
        url(r"^backend/my-backend2/$",
            OtherBackendView.as_view(backend_name="my-backend2")),
    )

This example defines two URLs, one for each backend. You can make the Django
URL pattern whatever you like, but the convention is to make it ``backend/``
followed by the matching **backend name** from INSTALLED_BACKENDS and a final
``/``. You must also supply the same **backend name** to the backend view via the ``backend_name`` keyword argument. This example defines two backends named ``my-backend1`` and ``my-backend2``, matching our example :ref:`INSTALLED_BACKENDS <backend-settings>` above.


Example URL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

If you learn by example, you can follow these steps and test invoking a
received message with a few lines of Python. This example is intended to serve
as a simple example of configuring :ref:`INSTALLED_BACKENDS <backend-settings>`
and :ref:`Backend URLs <backend-urls>`.

1. Include the following in urls.py::

    from rapidsms.backends.http.views import GenericHttpBackendView

    urlpatterns = patterns('',
        url(r'^backends/http-backend/$',
        GenericHttpBackendView.as_view(backend_name='http-backend')),
    )

2. Include the following in settings.py::

    INSTALLED_BACKENDS = {
        "http-backend": {
            "ENGINE": "rapidsms.contrib.httptester.backend.HttpTesterCacheBackend",
        },
    }

3. Now in a Python shell::

    >>> import urllib
    >>> import urllib2
    >>> data = urllib.urlencode({'identity': '1112223333', 'text': 'echo hello'})
    >>> request = urllib2.urlopen('http://localhost:8000/backends/http-backend/', data)
    >>> request.code
    200
    >>> request.read()
    'OK'
