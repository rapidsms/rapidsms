#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import urllib, urllib2
import random, cgi

from threading import Thread
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class Client(object):
    PROTOCOL_VERSION = "SPOMSKY/0.91"
    
    
    class Server(ThreadingMixIn, HTTPServer):
        pass
    
    
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            
            # parse the form data (what
            # the hell *is* this junk?)
            form = cgi.FieldStorage(
                fp = self.rfile, 
                headers = self.headers,
                environ = {
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": self.headers["content-type"] })
            
            # if a callback has been registered (via
            # Client#subscribe), call it along with
            # the source (phone number), and contents
            if hasattr(self.server.spomsky_client, "callback"):
                self.server.spomsky_client.callback(
                    form["source"].value, form["body"].value)
            
            # always respond positively
            self.send_response(200)
            self.end_headers()
        
        # Does nothing except prevent HTTP
        # requests being echoed to the screen
        def log_request(*args):
            pass
    
    def __init__(self, server_host="localhost", server_port=8100, client_host="localhost", client_port=None):
    
        # copy the arguments into
        # their attrs unchecked (!!)
        self.server_host = server_host
        self.server_port = int(server_port)
        self.client_host = client_host
        
        # initialize attributes
        self.subscription_id = None
        self.server = None
        
        # if no client port was provided, randomly pick a
        # high one. this is a bad idea, since it can fail.
        # TODO: check that the port is available!
        self.client_port = int(client_port) if client_port else random.randrange(10000, 11000)
    
    
    def __url(self, path):
        return "http://%s:%d/%s" % (self.server_host, self.server_port, path)
    
    
    def send(self, destination, body):
        
        # build the POST form
        data = urllib.urlencode({
            "version": self.PROTOCOL_VERSION,
            "destination": destination,
            "body": body
        })
        
        try:
        
            # attempt to POST to spomskyd
            f = urllib2.urlopen(self.__url("send"), data)
            
            # read the response, even though we
            # don't care what it contains (for now)
            str = f.read()
            f.close()
        
        # urllib2 raises an exception on failure; we
        # don't want to blow up the whole process,
        # so just return false instead
        except:
            return False
        
        # nothing went bang
        return True


    def subscribe(self, callback):
        
        # if we are already
        # subscribed, abort
        if self.server:
            return False
        
        # note down the callback, to be called
        # when a message arrives from the server
        self.callback = callback
        
        # create an HTTP server (to listen for callbacks from
        # the spomsky server, to notify us of incoming SMS)
        self.server = self.Server(("", self.client_port), self.RequestHandler)
        self.server.spomsky_client = self
        
        # start the server in a separate thread, and daemonize it
        # to prevent it from hanging once the main thread terminates
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
        # build the POST form
        data = urllib.urlencode({
            "version": self.PROTOCOL_VERSION,
            "host": self.client_host,
            "port": self.client_port,
            "path": "receiver"
        })
        
        try:
        
            # post the request to spomskyd, and fetch the response
            f = urllib2.urlopen(self.__url("receive/subscribe"), data)
            str = f.read()
            f.close()
            
            # the subscription was successful, so store the uuid,
            # and return true to indicate that we're subscribed
            self.subscription_id = f.info()["x-subscription-uuid"]
            return True
        
        # something went wrong, so reset the
        # subscription id and return false
        except:
            self.subscription_id = None
            return False
        
    
    def unsubscribe(self):
        
        # if we are subscribed, then send an HTTP
        # POST request to spomskyd to instruct it
        # to stop sending us messages
        if self.subscription_id:
            
            # build the POST form
            data = urllib.urlencode({
                "version": self.PROTOCOL_VERSION,
                "uuid": self.subscription_id
            })
            
            try:
            
                # post the request to spomskyd, and fetch the response
                f = urllib2.urlopen(self.__url("receive/unsubscribe"), data)
                str = f.read()
                f.close()
            
            # request failed? no  big deal, we've
            # probably already been unsubscribed
            except:
                pass
        
        # unset instance vars
        self.callback = None
        self.server = None
        self.thread = None
        
        # what could possibly
        # have gone wrong?
        return True

