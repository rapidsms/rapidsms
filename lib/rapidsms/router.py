#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time, threading

class Router (object):
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

        workers = []
        # launch each backend in its own thread
        for backend in self.backends:
            worker = threading.Thread(target=backend.start)
            worker.start()
            workers.append(worker)

        # wait until we're asked to stop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass
            
        for backend in self.backends:
            backend.stop()
        
        for worker in workers:
            worker.join()

    def incoming(self, message):      
        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it                      
        for app in self.apps:                                        
            app.incoming(message)
            print "DISPATCHED INCOMING %s to %s" % (message, app)

    def outgoing(self, message):
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for app in self.apps:
            app.outgoing(message)
            print "DISPATCHED OUTGOING %s to %s" % (message, app)

        # now send the message out
        print "SENT MESSAGE %s to %s" % (message, message.backend)
        message.backend.send(message)
        
