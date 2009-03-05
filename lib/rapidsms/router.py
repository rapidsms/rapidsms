#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time, datetime
import threading

import component
import log

class Router (component.Receiver):
    incoming_phases = ('parse', 'handle', 'cleanup')
    outgoing_phases = ('outgoing',)

    def __init__(self):
        component.Receiver.__init__(self)
        self.backends = []
        self.apps = []
        self.logger = log.Logger()
        super(component.Receiver,self).__init__()

    def log(self, level, msg, *args):
        self.logger.write(self, level, msg, *args)

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
                self.error("%s raised exception: %s" % (backend.name,e))
                time.sleep(5)
                self.error("restarting %s" % (backend.name,))

    def start (self):
        # dump some debug info for now
        self.info("BACKENDS: %r" % (self.backends))
        self.info("APPS: %r" % (self.apps))
        self.info("SERVING FOREVER...")
        
        # call the "start" method of each app
        for app in self.apps:
            app.start()
        
        workers = []
        # launch each backend in its own thread
        for backend in self.backends:
            worker = threading.Thread(target=self.start_backend, args=(backend,))
            worker.start()
            workers.append(worker)

        # wait until we're asked to stop
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            
        for backend in self.backends:
            backend.stop()
        
        for worker in workers:
            worker.join()

    def run(self):
        while self.message_waiting:
            msg = self.next_message(timeout=1.0)
            if msg is not None:
                self.incoming(msg)

    def incoming(self, message):   
        self.info("Incoming message: %r" % (message))
           
        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it                      
        for phase in self.incoming_phases:
            for app in self.apps:
                getattr(app, phase)(message)

    def outgoing(self, message):
        self.info("Outgoing message: %r" % (message))
        
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for phase in self.outgoing_phases:
            for app in self.apps:
                getattr(app, phase)(message)

        # now send the message out
        self.info("SENT MESSAGE %s to %s" % (message, message.backend))
        message.backend.send(message)
        
