# vim: ai ts=4 sts=4 et sw=4
from rapidsms.backends.http import RapidHttpBacked

import copy
import urllib
import urllib2
from datetime import datetime

from django.http import HttpResponse, HttpResponseBadRequest

class KannelBackend(RapidHttpBacked):
    """
    Backend for use with the Kannel SMS Gateway.
    
    The associated Kannel settings might look something like this:
    
    # listen for outgoing messages from RapidSMS:
    group = smsbox
    sendsms-port = 13013
    # .... other smsbox options here
    
    # deliver inbound messages to RapidSMS:
    group = sms-service
    keyword = default
    # don't send an automated reply here (it'll come through sendsms):
    max-messages = 0
    get-url = http://127.0.0.1:8888/?id=%p&text=%a
    """

    def configure(self, sendsms_url='http://127.0.0.1:13013/cgi-bin/sendsms',
                  sendsms_params=None, charset=None, coding=None,
                  encode_errors=None, **kwargs):
        self.sendsms_url = sendsms_url
        self.sendsms_params = sendsms_params or {}
        self.charset = charset or 'ascii'
        self.coding = coding or 0
        self.encode_errors = encode_errors or 'ignore'
        super(KannelBackend, self).configure(**kwargs)

    def handle_request(self, request):
        self.debug('Received request: %s' % request.GET)
        sms = request.GET.get('text', None)
        sender = request.GET.get('id', None)
        coding = request.GET.get('coding', None)
        charset = request.GET.get('charset', None)
        if sms is None or sender is None:
            error_msg = 'ERROR: Missing "text" or "id" params. '\
                        'parameters received are: %(params)s' % \
                         {'params': unicode(request.GET)}
            self.error(error_msg)
            return HttpResponseBadRequest(error_msg)
        now = datetime.utcnow()
        # UTF-8 (and possible other charsets) will already be decoded, while
        # UTF-16BE will not, so decode them manually here if we don't already
        # have a unicode string
        if charset and not isinstance(sms, unicode):
            sms = sms.decode(charset)
        try:
            msg = super(RapidHttpBacked, self).message(sender, sms, now)
        except:
            self.exception('failed to create message in RapidSMS')
            raise
        self.route(msg)
        return HttpResponse('') # any response would get sent to the user

    def send(self, message):
        self.info('Sending message: %s' % message)
        url_args = copy.copy(self.sendsms_params)
        url_args['to'] = message.connection.identity
        url_args['text'] = message.text.encode(self.charset,
                                               self.encode_errors)
        url_args['coding'] = self.coding
        url_args['charset'] = self.charset
        url = '?'.join([self.sendsms_url, urllib.urlencode(url_args)])
        try:
            self.debug('Opening URL: %s' % url)
            response = urllib2.urlopen(url)
        except:
            self.exception('Failed to send message')
            return
        self.info('SENT')
        self.debug('response body: %s' % response.read())
