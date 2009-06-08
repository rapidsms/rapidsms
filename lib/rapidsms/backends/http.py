#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer, SocketServer
import select
import random
import re
import urllib
import httphandlers as handlers
import rapidsms
from rapidsms.message import Message

msg_store = {}

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

    def do_GET(self):
        global msg_store
        # if the path is just "/" then start a new session
        # and redirect to that session's URL
        if self.path == "/":
            session_id = random.randint(100000, 999999)
            self.send_response(301)
            self.send_header("Location", "/%d/" % session_id)
            self.end_headers()
            return
        
        # if the path is of the form /integer/blah 
        # send a new message from integer with content blah
        send_regex = re.compile(r"^(?:/([a-zA-Z]\w*))?/([^/]+)/([^/]+)$")
        match = send_regex.match(self.path)
        if match:
            # send the message
            backend = match.group(1)
            session_id = match.group(2)
            text = match.group(3)
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if msg_store.has_key(session_id) and len(msg_store[session_id]):
                        self.wfile.write("{'phone':'%s', 'message':'%s'}" % (session_id, str(msg_store[session_id].pop(0))))
                return
                
            if backend:
                target = self.server.backend.router.get_backend(backend)
            else:
                target = self.server.backend
            # TODO watch out because urllib.unquote will blow up on unicode text 
            session_id, text = map(urllib.unquote_plus, (session_id, text))
            msg = target.message(session_id, text)
            target.route(msg)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("{'backend': '%s', 'phone':'%s', 'message':'%s'}" % (target.name, session_id, urllib.unquote(text)))
        else:
            self.log_error("Unhandled request: %s", self.path)
            
        return
        
    def do_POST(self):
        # TODO move the actual sending over to here
        return

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
        
        # also set it in the handler class so we can callback
        self.handler.backend = self
        
        # set the slug based on the handler, so we can have multiple
        # http backends
        self._slug = "http_%s" % handler  
        
    def run (self):
        while self.running:
            if self.message_waiting:
                msg = self.next_message()
                self.handler.outgoing(msg)
                
            self.server.handle_request()
