#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import BaseHTTPServer
import thread
from backend_base import Base


class Http(Base):
    
    class HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.path)
            return
            
        def do_POST(self):
            return
    
    def __init__(self, router, host="localhost", port=8000):
        self.server = BaseHTTPServer.HTTPServer((host, port), self.HttpHandler)
        self.router = router
        thread.start_new_thread(self.__serve_forever, ())
        
    def __serve_forever(self):
        print "Http backend up and running..."
        self.server.serve_forever()
