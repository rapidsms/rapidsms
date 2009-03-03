#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

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
        # dump some debug info for now
        print "BACKENDS: %r" % (self.backends)
        print "APPS: %r" % (self.apps)
        print "SERVING FOREVER..."

        # block forever! TODO: replace this
        # with a thread for each backend
        while(True):
            time.sleep(1)

    def dispatch_incoming(self, message):      
        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it                      
        for app in self.apps:                                        
            try:
                app.incoming(message)
                print "DISPATCHED INCOMING %s to %s" % (message, app)
            except AttributeError:
                # if the app does not care about incoming
                # messages then just fail silently
                pass                                                 
    
    def dispatch_outgoing(self, message):
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for app in self.apps:
            try:
                app.outgoing(message)
                print "DISPATCHED OUTGOING %s to %s" % (message, app)
            except AttributeError:
                # if the app does not care about outgoing
                # messages then just fail silently
                pass

        # now send the message out
        print "SENT MESSAGE %s to %s" % (message, message.backend)
        message.backend.send(message)
        
