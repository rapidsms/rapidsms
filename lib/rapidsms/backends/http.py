#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import BaseHTTPServer, SocketServer
import select
import httphandlers as handlers
import rapidsms

class HttpServer (BaseHTTPServer.HTTPServer, SocketServer.ThreadingMixIn):
    
    def handle_request (self, timeout=1.0):
        # don't block on handle_request
        reads, writes, errors = (self,), (), ()
        reads, writes, errors = select.select(reads, writes, errors, timeout)
        if reads:
            BaseHTTPServer.HTTPServer.handle_request(self)

class Backend(rapidsms.backends.Backend):
    def configure(self, host="localhost", port=8080, handler="HttpHandler"):
        
        #module_name = "httphandlers"
        #module = __import__(module_name, {}, {}, [''])
        component_class = getattr(handlers, handler)
        
        self.handler = component_class
        self.server = HttpServer((host, int(port)), component_class)
        self.type = "HTTP"
        # set this backend in the server instance so it 
        # can callback when a message is received
        self.server.backend = self
        
        # set the slug based on the handler, so we can have multiple
        # http backends
        self._slug = "http_%s" % handler  
        
    def run (self):
        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                self.handler.outgoing(msg)
            self.server.handle_request()
