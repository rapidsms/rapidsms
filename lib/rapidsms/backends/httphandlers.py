#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer, SocketServer
import select
import random
import re
import urllib
from datetime import datetime

import rapidsms
from rapidsms.message import Message

msg_store = {}

class RapidBaseHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def log_error (self, format, *args):
        self.server.backend.error(format, *args)

    def log_message (self, format, *args):
        self.server.backend.debug(format, *args)

     
class HttpHandler(RapidBaseHttpHandler):
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
        send_regex = re.compile(r"^/(\d+)/(.*)")
        match = send_regex.match(self.path)
        if match:
            # send the message
            session_id = match.group(1)
            text = match.group(2)
            
            if text == "json_resp":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                if msg_store.has_key(session_id) and len(msg_store[session_id]):
                        self.wfile.write("{'phone':'%s', 'message':'%s'}" % (session_id, str(msg_store[session_id].pop(0))))
                return
                
            # TODO watch out because urllib.unquote will blow up on unicode text 
            msg = self.server.backend.message(session_id, urllib.unquote(text))
            self.server.backend.route(msg)
            # respond with the number and text 
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("{'phone':'%s', 'message':'%s'}" % (session_id, urllib.unquote(text)))
            return
            
        return
        
    def do_POST(self):
        # TODO move the actual sending over to here
        return

class MTechHandler(RapidBaseHttpHandler):
    '''An HttpHandler for the mtech gateway, for use in Nigeria''' 
    def do_GET(self):
        global msg_store
        querystart = self.path.find("?")
        if querystart == -1:
            self.respond(500, "Must specify parameters in the URL!")
            return
        
        query_params = map((lambda t: t.split("=")), self.path[querystart + 1:].split("&"))
        
        self.accept_message(query_params)
        
        
    def do_POST(self):
        if self.rfile:
            content_len = int(self.headers["Content-Length"])
            data = self.rfile.read(content_len)
            params = map((lambda t: t.split("=")), data.split("&"))
            self.accept_message(params)
    
    def respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(msg)

    def accept_message(self, params):
        # parameters are: 
        # text=message%20body
        # from=2347067277331
        # sent=200904091443.21
        # mtech_received=200904091444.48
        # operator_received=200904091444.4
        
        text = None
        sender = None
        date = None
        for param in params:
            if param[0] == "text":
                # TODO watch out because urllib.unquote will blow up on unicode text 
                text = urllib.unquote(param[1])
            elif param[0] == "from":
                sender = param[1]
            elif param[0] == "sent":
                date = datetime.strptime(param[1], "%Y%m%d%H%M.%S")
        
        if text and sender: 
            # respond with the number and text 
            msg = self.server.backend.message(text, sender, date)
            self.server.backend.route(msg)
            self.respond(200, "{'phone':'%s', 'message':'%s'}" % (sender, text))
            return
        else:
            self.respond(500, "You must specify a valid number and message")
            return

        
