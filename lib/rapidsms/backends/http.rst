-*- restructuredtext -*-

RapidHttpBackend
===============

RapidHttpBackend is a basic extension to Django's built-in WSGI server
simplified to run as a backend for RapidSMS.

Configuration
--------------
To use the http backend, one needs to append 'http' to the list of 
available backends, like so:

    "my_http_backend" : {"ENGINE":  "rapidsms.backends.http", 
                "port": 8888,
                "gateway_url": "http://www.smsgateway.com",
                "params_outgoing": "user=my_username&password=my_password&id=%(phone_number)s&text=%(message)s",
                "params_incoming": "id=%(phone_number)s&text=%(message)s"
        }

'params_outgoing' must have %(message)s and %(phone_number)s as values in the key-value pairs. 
These will be substituted for the message.text and message.connection.identity respectively.

'params_incoming' must have %(message)s and %(phone_number)s as values in the key-value pairs. 
This format demonstrates how the http handler expects to receive those parameters from an external server
via HTTP GET.

Extension
--------------

To further customize the behaviour of httpbackend, simply extend rapidsms.backends.http.RapidHttpBackend
and implement handle_request. For example::

    import datetime
	import twilio
    
    from django.http import HttpResponse
    from rapidsms.backends.http import RapidHttpBackend


    class MyBackend(RapidHttpBackend):
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
	
	    def send(self, message):
	        self.info('Sending message: %s' % message)
	        data = {
	            'From': self.config['number'],
	            'To': message.connection.identity,
	            'Body': message.text,
	        }
	        if 'callback' in self.config:
	            data['StatusCallback'] = self.config['callback']
	        self.debug('POST data: %s' % pprint.pformat(data))
	        url = '/%s/Accounts/%s/SMS/Messages' % (self.api_version,
	                                                self.config['account_sid'])
	        try:
	            response = self.account.request(url, 'POST', data)
	        except Exception, e:
	            self.exception(e.read())
	            response = None
	        if response:
	            self.info('SENT')
	            self.debug(response)