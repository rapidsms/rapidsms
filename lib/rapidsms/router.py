#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import spomsky
import time

class Router:
    def __init__(self):
        self.backends = []
        self.apps = []

    def add_app(self, app):
        self.apps.append(app)

    def add_backend(self, backend):
        self.backends.append(backend)

    def serve_forever(self):

        # if no backends have been set up, add one with
        # no arguments, for local dev and debugging
        if len(self.backends) == 0:
            #spomsky Client needs something for host and port
            self.add_backend(spomsky.Client(None,None))

        # dump some debug info for now
        print "BACKENDS: %r" % (self.backends)
        print "APPS: %r" % (self.apps)
        print "SERVING FOREVER..."

        # block forever! TODO: replace this
        # with a thread for each backend
        while(True):
            time.sleep(1)

    def receive(self, message):
        for app in self.apps:
            app.receive(message)

    def register_app(self, app):
        #bare minimum needed to succeed at test
        pass 
