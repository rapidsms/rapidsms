#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import time, datetime
import threading

import component
import log

class Router (component.Receiver):
    incoming_phases = ('parse', 'handle', 'cleanup')
    outgoing_phases = ('outgoing',)

    def __init__(self, conf):
        component.Receiver.__init__(self)
        self.backends = []
        self.apps = []
        self.running = False
        self.logger = None
        super(component.Receiver,self).__init__()
        self.__configure(conf)

    def log(self, level, msg, *args):
        self.logger.write(self, level, msg, *args)


    def add_app (self, app_name):
        """Imports and instantiates an application, given its name.
           Application classes are assumed to be named "App", in the
           module "apps.{app_name}.app" """
        
        # resolve the app name into a real class
        app_module_str = "apps.%s.app" % (app_name)
        app_module = __import__(app_module_str, {}, {}, [''])
        app_class = app_module.App
        
        # create the application with an instance of this router
        # and keep hold of it here, so we can communicate both ways
        app_instance = app_class(self)
        self.apps.append(app_instance)


    def add_backend (self, backend_name):
        """Imports and instantiates a backend, given its name. Backend
           classes are assumed to be named as the capitalized form of
           their module name, which is "rapidsms.backend.{backend_name}"""
        
        # resolve the backend into a real class
        backend_module_str = "rapidsms.backends.%s" % (backend_name)
        backend_module = __import__(backend_module_str, {}, {}, [''])
        backend_class = backend_module.Backend 
        
        # create the backend with an instance of this router and
        # keep hold of it here, so we can communicate both ways
        backend_instance = backend_class(self)
        self.backends.append(backend_instance)
    
    
    def start_backend (self, backend):
        while self.running:
            try:
                # start the backend
                backend.start()
                # if backend execution completed normally, end the thread
                break
            except Exception, e:
                # an exception was raised in backend.start()
                # sleep for 5 seconds, then loop and restart it
                self.error("%s failed: %s" % (backend.name,e))
                if not self.running: break
                time.sleep(5.0)
                self.error("restarting %s" % (backend.name,))

    def start (self):
        self.running = True

        # dump some debug info for now
        self.info("BACKENDS: %r" % (self.backends))
        self.info("APPS: %r" % (self.apps))
        self.info("SERVING FOREVER...")
        
        # call the "start" method of each app
        for app in self.apps:
            try:
                app.start()
            except Exception, e:
                self.error("%s failed on start: %r", app, e)

        workers = []
        # launch each backend in its own thread
        for backend in self.backends:
            worker = threading.Thread(target=self.start_backend, args=(backend,))
            worker.start()
            workers.append(worker)

        # call the "start" method of each app
        for app in self.apps:
            app.start()
        
        # wait until we're asked to stop
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            
        self.running = False
        for backend in self.backends:
            try:
                backend.stop()
            except Exception, e:
                self.error("%s failed on stop: %s" % (backend.name,e))
        
        for worker in workers:
            worker.join()


    def run(self):
        msg = self.next_message(timeout=1.0)
        if msg is not None:
            self.incoming(msg)

    def incoming(self, message):   
        self.info("Incoming message via %s: %s ->'%s'" %\
			(message.backend.name, message.caller, message.text))
           
        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it                      
        for phase in self.incoming_phases:
            for app in self.apps:
                self.debug('IN' + ' ' + phase + ' ' + app.name)
                try:
                    getattr(app, phase)(message)
                except Exception, e:
                    self.error("%s failed on %s: %r", app, phase, e)

    def outgoing(self, message):
        self.info("Outgoing message via %s: %s <- '%s'" %\
			(message.backend.name, message.caller, message.text))
        
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for phase in self.outgoing_phases:
            for app in self.apps:
                self.debug('OUT' + ' ' + phase + ' ' + app.name)
                try:
                    getattr(app, phase)(message)
                except Exception, e:
                    self.error("%s failed on %s: %r", app, phase, e)

        # now send the message out
        message.backend.send(message)
        self.info("SENT message '%s' to %s via %s" % (message.text,\
			message.caller, message.backend.name))\
        
    def __configure(self, conf):
        level, file = conf["log"]["level"], conf["log"]["file"]
        self.logger = log.Logger(level, file)
 
        for app_class in conf["rapidsms"]["apps"]:
            self.info("Adding app: %r" % app_class)
            self.add_app(app_class)

        for backend_class in conf["rapidsms"]["backends"]:
            self.info("Adding backend: %r" % backend_class)
            self.add_backend(backend_class)

