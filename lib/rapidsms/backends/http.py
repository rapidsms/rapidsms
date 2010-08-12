import select

from django import http
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


class RapidHttpBacked(BackendBase):
    """ RapidSMS backend that creates and handles an HTTP server """

    def configure(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.handler = RapidWSGIHandler()
        self.handler.backend = self

    def run(self):
        server_address = (self.host, int(self.port))
        self.info('Starting HTTP server on {0}:{1}'.format(*server_address))
        self.server = RapidHttpServer(server_address, WSGIRequestHandler)
        self.server.set_app(self.handler)
        while self.running:
            self.server.handle_request()

    def handle_request(self, request):
        """ Override this in a subclass to create and route messages """
        return http.HttpResponse('OK')
