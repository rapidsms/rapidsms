#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time
import threading

import log

class Router (object):
    incoming_phases = ('parse', 'handle', 'cleanup')
    outgoing_phases = ('outgoing',)

    def __init__(self):
        self.backends = []
        self.apps = []
        self.log = log.Log()

    def log(self, level, message):
        # call the function "level" on self.log
        # (used by components)
        getattr(self.log, level)(message)

    def add_app (self, app):
        self.apps.append(app)

    def add_backend (self, backend):
        self.backends.append(backend)

    def start_backend (self, backend):
        while True:
            try:
                # start the backend
                backend.start()
                # if backend execution completed normally, end the thread
                break
            except Exception, e:
                # an exception was raised in backend.start()
                # sleep for 5 seconds, then loop and restart it
                self.log.error("%s raised exception: %s" % (backend,e))
                time.sleep(5)
                self.log.error("restarting %s" % (backend,))

    def start (self):
        # dump some debug info for now
        self.log.info("BACKENDS: %r" % (self.backends))
        self.log.info("APPS: %r" % (self.apps))
        self.log.info("SERVING FOREVER...")

        workers = []
        # launch each backend in its own thread
        for backend in self.backends:
            worker = threading.Thread(target=start_backend, args=(backend,))
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
        for phase in self.incoming_phases:
            for app in self.apps:                                        
                getattr(app, phase)(message)

    def outgoing(self, message):
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for phase in self.outgoing_phases:
            for app in self.apps:
                getattr(app, phase)(message)

        # now send the message out
        self.log.info("SENT MESSAGE %s to %s" % (message, message.backend))
        message.backend.send(message)
        
