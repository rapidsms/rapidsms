#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer, SocketServer
import select
import random
import re

from backend import Backend
from rapidsms.message import Message

class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
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
        send_regex = re.compile(r"^/(\d{6})/(.*)")
        match = send_regex.match(self.path)
        if match:
            # send the message
            session_id = match.group(1)
            text = match.group(2)
            # TODO unescape the text (i.e. %20 => " ") 
            self.server.backend.receive(session_id, text)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("Number: %s<br>Message: %s" % (session_id, text))
            return
            
        return
        
    def do_POST(self):
        # TODO move the actual sending over to here
        return

class HttpServer (SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def handle_request (self, timeout=1.0):
        # don't block on handle_request
        reads, writes, errors = (self,), (), ()
        reads, writes, errors = select.select(reads, writes, errors, timeout)
        if reads:
            super(self)

class Http(Backend):
    def __init__(self, router, host="localhost", port=8080):
        self.server = HttpServer((host, port), HttpHandler)
        # set this backend in the server instance so it 
        # can callback when a message is received
        self.server.backend = self
        self.router = router
        
    def run (self):
        while self.running:
            if self.has_outgoing:
                msg = self.outgoing()
                # oops we have to throw the message away
            self.handle_request()
