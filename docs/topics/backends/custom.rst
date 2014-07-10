.. _custom-backends:

Custom Backends
===============

You can create a custom backend if the supplied backends don't suffice. Since backends handle both inbound and outbound communication, the following section is divided into :ref:`custom-backends-incoming-messages` and
:ref:`custom-backends-outgoing-messages`, respectively.

The built-in Vumi and Kannel backends use the methods described below, so you can review the `source code <https://github.com/rapidsms/rapidsms/tree/master/rapidsms/backends>`_ to see actual implementation examples.

For a more general backend overview, please see :ref:`rapidsms-backends`.


.. _custom-backends-incoming-messages:

Incoming Messages
-----------------


.. _http-backend:

HTTP Backend
************

RapidSMS provides a base suite of HTTP views and forms to help simplify backend
creation in ``rapidsms.backends.http``. These are useful for standardizing
incoming message handling. They can be extended for use in your own backends. The :ref:`http-backend` powers both the :ref:`Vumi <vumi-backend>` and :ref:`Kannel <kannel-backend>` backends.

You can, of course, simply write your own Django views to handle incoming
messages if the supplied classes do not provide enough flexibility.


Incoming message life cycle
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, when RapidSMS receives a message over HTTP, it's processed in the
following way:

1. Data from a text message is received by Django over an HTTP request.
2. The HTTP request is routed through a :ref:`Backend URL <backend-urls>`.
3. This backend view takes the HTTP request and passes it into a backend form.
4. This backend form cleans the message data and checks its validity.
5. If the message is valid, message data is sent to the router for processing via :func:`rapidsms.router.receive`.
6. An HTTP response is sent to the HTTP request sender with an HTTP status code to indicate that the message was received and passed to the router for processing successfully or that there was an error.

The HTTP response from a backend view does not necessarily indicate that the
resulting messages were sent by the router, only that the incoming message was
added to the queue for processing.


GenericHttpBackendView
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: rapidsms.backends.http.views.GenericHttpBackendView
    :members: http_method_names, params

The simplest type of custom backend is an HTTP backend that needs to accept
parameters other than ``identity`` and ``text``. To create such a custom
backend, one can subclass the ``GenericHttpBackendView`` as follows::

    from rapidsms.backends.http.views import GenericHttpBackendView

    class MyBackendView(GenericHttpBackendView):
        params = {
            'identity_name': 'phone',
            'text_name': 'message',
        }

The ``params`` dictionary contains key value pairs that map internal names to
the keys used in requests to the backend. In the above example, an HTTP request
would provide ``phone`` and ``message`` parameters.

An URL pattern for this backend might look like::

    from project_name.app_name.views import MyBackendView

    urlpatterns = patterns('',
        url(r'^backends/mybackend/$',
            MyBackendView.as_view(backend_name='mybackend')),
    )

A request to this backend might look like the following::

    >>> import urllib
    >>> import urllib2
    >>> data = urllib.urlencode({'phone': '1112223333', 'message': 'ping'})
    >>> request = urllib2.urlopen('http://localhost:8000/backends/mybackend/', data)
    >>> request.code
    200
    >>> request.read()
    'OK'


Custom Validation
~~~~~~~~~~~~~~~~~

Another custom backend might necessitate handling more parameters in the
request, or validating the incoming data differently.  A convenient way
to do this validation with Django is with forms::

    from .forms import ExtraParamsHttpBackendForm
    from rapidsms.backends.http.views import GenericHttpBackendView

    class ExtraParamsHttpBackendView(GenericHttpBackendView):
        form_class = ExtraParamsHttpBackendForm

This example application would have the following forms definition::

    from django import forms
    from rapidsms.backends.http.forms import BaseHttpForm

    class ExtraParamsHttpBackendForm(BaseHttpForm):
        extra = forms.TextField()

        def get_incoming_data(self):
            fields = self.cleaned_data.copy()
            return {'identity': self.cleaned_data['identity_name'],
                    'text': self.cleaned_data['text_name'],
                    'extra': self.cleaned_data['extra']}

This uses RapidSMS's BaseHttpForm:

.. autoclass:: rapidsms.backends.http.forms.BaseHttpForm
    :members:

Data coming into this backend would require an ``extra`` parameter, which would
be passed onto the message queue.

Alternatively, here's an example of a backend form with custom validation::

    from django import forms
    from rapidsms.backends.http.forms import BaseHttpForm

    MY_NUMBER = '1231231234'

    class OnlyTextMeHttpBackendForm(BaseHttpForm):

        def clean_text_name():
            text_name = self.cleaned_data.get('text_name')
            if text_name != MY_NUMBER:
                raise forms.ValidationError(
                    'SMS received from number other than {0}'.format(MY_NUMBER)
                )
            return text_name


.. _custom-backends-outgoing-messages:

Outgoing Messages
-----------------


BackendBase
***********

Similar to :ref:`http-backend` for incoming messages, ``BackendBase`` provides
the foundation for outbound functionality. All backends will typically extend
this base class. This class will be passed the configuration dictionary 
defined in :ref:`Backend Settings <backend-settings>`.

.. autoclass:: rapidsms.backends.base.BackendBase
    :members: send, configure, model, find

