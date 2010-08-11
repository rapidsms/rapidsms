-*- restructuredtext -*-

RapidHttpBacked
===============

RapidHttpBacked is a basic extension to Django's built-in WSGI server
simplified to run as a backend for RapidSMS.

Implementation
--------------

To create a new backend, simply extend rapidsms.backends.http.RapidHttpBacked
and implement handle_request. For example::

    import datetime

    from django.http import HttpResponse
    from rapidsms.backends.http import RapidHttpBacked


    class MyBackend(RapidHttpBacked):
        """ A RapidSMS backend for the My Cool SMS API """

        def configure(self, config=None, **kwargs):
            self.config = config
            super(MyBackend, self).configure(**kwargs)

        def handle_request(self, request):
            self.debug('Request: %s' % request.POST)
            message = self.message(request.POST)
            if message:
                self.route(message)
            return HttpResponse('OK')

        def message(self, data):
            sms = data.get('from', '')
            sender = data.get('text', '')
            if not sms or not sender:
                self.error('Missing from or text: %s' % data)
                return None
            now = datetime.datetime.utcnow()
            return super(MyBackend, self).message(sender, sms, now)
