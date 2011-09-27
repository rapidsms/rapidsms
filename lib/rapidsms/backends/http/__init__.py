#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
To use the http backend, one needs to append 'http' to the list of 
available backends, like so:

    "my_http_backend" : {"ENGINE":  "rapidsms.backends.http", 
                "port": 8888,
                "gateway_url": "http://www.smsgateway.com",
                "params_outgoing": "user=my_username&password=my_password&id=%(phone_number)s&text=%(message)s",
                "params_incoming": "id=%(phone_number)s&text=%(message)s"
        }

"""

import urllib2
import select
from datetime import datetime

from django import http
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.handlers.wsgi import WSGIHandler, STATUS_CODE_TEXT
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler

from rapidsms.log.mixin import LoggerMixin
from rapidsms.backends.base import BackendBase


class RapidWSGIHandler(WSGIHandler, LoggerMixin):
    """ WSGIHandler without Django middleware and signal calls """

    def _logger_name(self):
        return "%s/%s" % (self.backend._logger_name(), 'handler')

    def __call__(self, environ, start_response):
        request = self.request_class(environ)
        self.debug('Request from %s' % request.get_host())
        try:
            response = self.backend.handle_request(request)
        except Exception, e:
            self.exception(e)
            response = http.HttpResponseServerError()
        try:
            status_text = STATUS_CODE_TEXT[response.status_code]
        except KeyError:
            status_text = 'UNKNOWN STATUS CODE'
        status = '%s %s' % (response.status_code, status_text)
        response_headers = [(str(k), str(v)) for k, v in response.items()]
        start_response(status, response_headers)
        return response


class RapidHttpServer(WSGIServer):
    """ WSGIServer that doesn't block on handle_request """

    def handle_request(self, timeout=1.0):
        reads, writes, errors = (self, ), (), ()
        reads, writes, errors = select.select(reads, writes, errors, timeout)
        if reads:
            WSGIServer.handle_request(self)


class RapidHttpBackend(BackendBase):
    """ RapidSMS backend that creates and handles an HTTP server """

    _title = "HTTP"

    def configure(self, host="localhost", port=8080, 
                  gateway_url="http://smsgateway.com", 
                  params_outgoing="user=my_username&password=my_password&id=%(phone_number)s&text=%(message)s", 
                  params_incoming="id=%(phone_number)s&text=%(message)s"):
        self.host = host
        self.port = port
        self.handler = RapidWSGIHandler()
        self.handler.backend = self
        self.gateway_url = gateway_url
        self.http_params_outgoing = params_outgoing
        
        self.incoming_phone_number_param = None
        self.incoming_message_param = None
        key_value = params_incoming.split('&')
        for kv in key_value:
            key,val = kv.split('=')
            if val == "%(phone_number)s": 
                self.incoming_phone_number_param = key
            elif val == "%(message)s":
                self.incoming_message_param = key

    def run(self):
        server_address = (self.host, int(self.port))
        self.info('Starting HTTP server on {0}:{1}'.format(*server_address))
        self.server = RapidHttpServer(server_address, WSGIRequestHandler)
        self.server.set_app(self.handler)
        while self.running:
            self.server.handle_request()

    def handle_request(self, request):
        self.debug('Received request: %s' % request.GET)
        sms = request.GET.get(self.incoming_message_param, '')
        sender = request.GET.get(self.incoming_phone_number_param, '')
        if not sms or not sender:
            error_msg = 'ERROR: Missing %(msg)s or %(phone_number)s. parameters received are: %(params)s' % \
                         { 'msg' : self.incoming_message_param, 
                           'phone_number': self.incoming_phone_number_param,
                           'params': unicode(request.GET)
                         }
            self.error(error_msg)
            return HttpResponseBadRequest(error_msg)
        now = datetime.utcnow()
        try:
            msg = super(RapidHttpBackend, self).message(sender, sms, now)
        except Exception, e:
            self.exception(e)
            raise        
        self.route(msg)
        return HttpResponse('OK') 
    
    def send(self, message):
        self.info('Sending message: %s' % message)
        # if you wanted to add timestamp or any other outbound variable, 
        # you could add it to this context dictionary
        context = {'message':message.text,
                   'phone_number':message.connection.identity}
        url = "%s?%s" % (self.gateway_url, self.http_params_outgoing % context)
        try:
            self.debug('Sending: %s' % url)
            response = urllib2.urlopen(url)
        except Exception, e:
            self.exception(e)
            return
        self.info('SENT')
        self.debug(response)
