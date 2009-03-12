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
        self.running = False
        self.logger = None
        super(component.Receiver,self).__init__()

    def log(self, level, msg, *args):
        self.logger.write(self, level, msg, *args)

    def set_logger(self, level, file):
        self.logger = log.Logger(level, file)

    def build_component (self, class_template, conf):
        """Imports and instantiates an module, given a dict with 
           the config key/value pairs to pass along."""
        # break the class name off the end of the module template
        # i.e. "apps.%s.app.App" -> ("apps.%s.app", "App")
        module_template, class_name = class_template.rsplit(".",1)
       
        # make a copy of the conf dict so we can delete from it
        conf = conf.copy()

        # resolve the component name into a real class
        module_name = module_template % (conf.pop("type"))
        module = __import__(module_name, {}, {}, [''])
        component = getattr(module, class_name)
        
        # create the component with an instance of this router
        # and keep hold of it here, so we can communicate both ways
        title = conf.pop("title")
        try:
            return component(title, self, **conf)
        except TypeError, e:
            # "__init__() got an unexpected keyword argument '...'"
            missing_keyword = e.message.split("'")[1]
            raise Exception("Component '%s' does not support a '%s' option."
                    % (title, missing_keyword))

    def add_backend (self, conf):
        backend = self.build_component("rapidsms.backends.%s.Backend", conf)
        self.backends.append(backend)

    def add_app (self, conf):
        app = self.build_component("apps.%s.app.App", conf)
        self.backends.append(app)
    
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
