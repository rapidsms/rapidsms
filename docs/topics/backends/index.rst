RapidSMS Backends
=================

.. module:: rapidsms.backends

Overview
-----------------

Backends are used to define the way RapidSMS sends messages over an external source. To handle incoming requests, RapidSMS backends make use of Django url routing and class based views to handle incoming HTTP requests, which contain data from SMS messages. When messages are received by a RapidSMS project, they are handled in the following workflow:

1. Data from a text message is received over an HTTP request.
2. The HTTP request is routed through an urls.py module. Each url pattern is paired directly with the backend view to be used for processing.
3. This backend view takes the HTTP request and passes it into a backend form.
4. This backend form cleans the message data and checks its validity.
5. If the message is valid, message data is sent to the RapidSMS router for delivery via the :doc:`messaging API </topics/router/messaging>` . The router will send outgoing messages through the channels defined by the backend.
6. An HTTP response is sent to the HTTP request sender with an HTTP status code to indicate that the message was recieved and passed to the router for processing successfully or that there was an error.

N.B. - The HTTP response from a backend view does not necessarily indicate that the resulting SMS messages were sent by the router, only that the incoming message was added to the queue for processing.


Configuration
-------------

Backends for a RapidSMS project are configured in settings.py as well as one or more urls.py files. The following is a general description of this seperation::

1. The settings.py configuration defines a list of backends to use, each with a unique name and a python path to the backend module to use.
   The same backend module can be included more than once, each with a unique backend name.
2. The urls.py file(s) define the endpoints that accept HTTP requests and the backend names (as defined in settings.py) that handle each.

The backend settings configuration is accomplished in the :setting:`INSTALLED_BACKENDS` setting.

An example urls.py pattern that routes backend/kannel-fake-smsc/ to the 'kannel-fake-smsc' backend defined in settings.py is shown below::

    urlpatterns = patterns('',
        # ...
        url(r"^backend/kannel-fake-smsc/$",
            KannelBackendView.as_view(backend_name="kannel-fake-smsc")),
    )

As this url pattern demonstrates, the declaration uses the Django URL pattern definitions to tie a backend to a particular URL. The backend_name kwarg is passed to the view and provides the name of the backend as provided in :setting:`INSTALLED_BACKENDS`. The convention is to route /backend/<backend_name>/ to its corresponding backend in :setting:`INSTALLED_BACKENDS`, but any unique URL pattern can be used.

See :ref:`kannel_configuration` for more information about setting up the kannel backend.


Backends That Ship with RapidSMS
--------------------------------

Some backends have been deprecated in 0.10 in favor of using HTTP based backends for improved testability and scalability. These include the bucket, GSM, email, IRC, and smpp backends.

Backends that come with the 0.10 version of RapidSMS include:

* `http backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/http.py>`_
* `kannel backend <http://github.com/rapidsms/rapidsms/blob/master/lib/rapidsms/backends/kannel.py>`_


Backends that do not ship with RapidSMS core, but are compatible with version 0.10 include:

* `twilio backend <https://github.com/caktus/rapidsms-twilio`_


Example Configuration
---------------------
The following is intended to serve as a simple example of configuring a backend in the settings.py and urls.py modules and testing it out with some HTTP requests.

* Include the following in urls.py::

    from rapidsms.backends.http.views import GenericHttpBackendView

    urlpatterns = patterns('',
        url(r'^backends/httptester/$', GenericHttpBackendView.as_view('httptester')),
    )

* Include the following in settings.py::

    INSTALLED_BACKENDS = {
        "httptester": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
    }

* Now in a python shell::

    >>> import urllib
    >>> import urllib2
    >>> data = urllib.urlencode({
        'identity': '1112223333', 'text': 'echo hello'})
    >>> request = urllib2.urlopen('http://localhost:8000/backends/httptester/', data)
    >>> request.code
    200
    >>> request.read()
    'OK'


Custom Backends
---------------

The simplest type of custom backend is an http backend that needs to accept parameters other than 'identity' and 'text'. To create such a custom backend, one can subclass the GenericHTTPBackendView as follows::

    from rapidsms.backends.http.views import GenericHttpBackendView

    class CustomHttpBackendView(GenericHttpBackendView):
        params = {
            'identity_name': 'phone',
            'text_name': 'message',
        }

The params dictionary contains key value pairs that map internal names to the keys used in requests to the backend. In the above example, an HTTP request would provide 'phone' and 'message' parameters.

This backend would be registered in :setting:`INSTALLED_BACKENDS` with::

    INSTALLED_BACKENDS = {
        "customhttp": {
            "ENGINE": "rapidsms.contrib.httptester.backend",
        },
    }

An URL pattern for this backend might look like::


    from project_name.app_name.views import CustomHttpBackendView

    urlpatterns = patterns('',
        url(r'^backends/httptester/$', CustomHttpBackendView.as_view('customhttp')),
    )

A request to this backend might look like the following::

    >>> import urllib
    >>> import urllib2
    >>> data = urllib.urlencode({
        'phone': '1112223333', 'message': 'ping'})
    >>> request = urllib2.urlopen(
            http://localhost:8000/backends/customhttp/', data)
    >>> request.code
    200
    >>> request.read()
    'OK'


Using Custom Backend Forms
--------------------

Another custom backend might neccesitate handling more parameters in the request, or validating the incoming data differently. Such a backend would need to use its own form and is demonstrated below::

    from .forms import ExtraParamsHttpBackendForm
    from rapidsms.backends.http.views import GenericHttpBackendView

    class ExtraParamsHttpBackendView(GenericHttpBackendView):
        form_class = ExtraParamsHttpBackendForm

forms.py in this application would have the following definition::

    from django import forms
    from rapidsms.backends.http.forms import BaseHttpForm

    class ExtraParamsHttpBackendForm(BaseHttpForm):
        extra = forms.TextField()

        def get_incoming_data(self):
            fields = self.cleaned_data.copy()
            return {'identity': self.cleaned_data['indentity_name'],
                    'text': self.cleaned_data['text_name'],
                    'extra': self.cleaned_data['extra']}

Data coming into this backend would require an 'extra' parameter, which would be passed onto the message queue.

An example of a backend form with custom validation is here::

    from django import forms
    from rapidsms.backends.http.forms import BaseHttpForm

    MY_NUMBER = '1231231234'

    class OnlyTextMeHttpBackendForm(BaseHttpForm):

        def clean_text_name:
            text_name = self.cleaned_data.get('text_name')
            if text_name != MY_NUMBER:
                raise forms.ValidationError(
                    'SMS received from number other than {0}'.format(MY_NUMBER)
                )
            return text_name
