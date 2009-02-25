#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer
import thread
import random
import re
from backend_base import Base


class Http(Base):
    
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
            
            # if the path is of the form /integer/blah we want
            # want to send a new message from integer with
            # content blah
            send_regex = re.compile(r"^/(\d{6})/(.*)")
            match = send_regex.match(self.path)
            if match:
                # send the message
                session_id = match.group(1)
                text = match.group(2)
                self.receive(session_id, text)
                # respond with the number and text 
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Number: %s<br>Message: %s" % (session_id, text))
                return
                
            return
            
        def do_POST(self):
            # TODO put this back in!
            #send_regex = re.compile("^/(\d{6})/send")
            #match = send_regex.match(self.path)
            #if match:
            #    # send the message to the router
            #    session_id = match.group(1)
            #    text = 
            #    self.receive(session_id, text)
            return
    
    def __init__(self, router, host="localhost", port=8000):
        self.server = BaseHTTPServer.HTTPServer((host, port), self.HttpHandler)
        self.router = router
        thread.start_new_thread(self.__serve_forever, ())
        
    def __serve_forever(self):
        print "Http backend up and running..."
        self.server.serve_forever()
