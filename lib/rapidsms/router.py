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
        component_class = getattr(module, class_name)
        
        # create the component with an instance of this router
        # and keep hold of it here, so we can communicate both ways
        title = conf.pop("title")
        component = component_class(title, self)
        try:
            component.configure(**conf)
        except TypeError, e:
            # "__init__() got an unexpected keyword argument '...'"
            if "unexpected keyword" in e.message:
                missing_keyword = e.message.split("'")[1]
                raise Exception("Component '%s' does not support a '%s' option."
                        % (title, missing_keyword))
            else:
                raise
        return component

    def add_backend (self, conf):
        backend = self.build_component("rapidsms.backends.%s.Backend", conf)
        self.backends.append(backend)

    def add_app (self, conf):
        app = self.build_component("apps.%s.app.App", conf)
        self.apps.append(app)
    
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

    def start_all_apps (self):
        # call the "start" method of each app
        for app in self.apps:
            try:
                app.start()
            except Exception, e:
                self.error("%s failed on start: %r", app, e)

    def start_all_backends (self):
        # launch each backend in its own thread
        for backend in self.backends:
            worker = threading.Thread(target=self.start_backend, args=(backend,))
            worker.start()

    def stop_all_backends (self):
        for backend in self.backends:
            try:
                backend.stop()
            except Exception, e:
                self.error("%s failed on stop: %s" % (backend.name,e))

    def start (self):
        self.running = True

        # dump some debug info for now
        self.info("BACKENDS: %r" % (self.backends))
        self.info("APPS: %r" % (self.apps))
        self.info("SERVING FOREVER...")
        
        self.start_all_backends()
        self.start_all_apps()

        # wait until we're asked to stop
        while self.running:
            try:
                self.run()
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
        
        self.stop_all_backends()
        self.running = False

    def stop (self):
        self.running = False
        
    def run(self):
        msg = self.next_message(timeout=1.0)
        if msg is not None:
            self.incoming(msg)

    def incoming(self, message):   
        self.info("Incoming message via %s: %s ->'%s'" %\
			(message.connection.backend.name, message.connection.identity, message.text))
           
        # loop through all of the apps and notify them of
        # the incoming message so that they all get a
        # chance to do what they will with it                      
        for phase in self.incoming_phases:
            for app in self.apps:
                self.debug('IN' + ' ' + phase + ' ' + app.name)
                responses = len(message.responses)
                handled = False
                try:
                    handled = getattr(app, phase)(message)
                except Exception, e:
                    self.error("%s failed on %s: %r", app, phase, e)
                if phase == 'handle':
                    if handled is True:
                        self.debug("%s short-circuited handle phase", app.name)
                        break
                elif responses != len(message.responses):
                    self.warn("App '%s' shouldn't send responses in %s()!", 
                        app.name, phase)

        # now send the message's responses
        message.flush_responses()

    def outgoing(self, message):
        self.info("Outgoing message via %s: %s <- '%s'" %\
			(message.connection.backend.name, message.connection.identity, message.text))
        
        # first notify all of the apps that want to know
        # about outgoing messages so that they can do what
        # they will before the message is actually sent
        for phase in self.outgoing_phases:
            continue_sending = True
			# call outgoing phases in the opposite order of the
			# incoming phases so that, for example, the first app
			# called with an incoming message is the last app called
			# with an outgoing message
            for app in reversed(self.apps):
                self.debug('OUT' + ' ' + phase + ' ' + app.name)
                try:
                    continue_sending = getattr(app, phase)(message)
                except Exception, e:
                    self.error("%s failed on %s: %r", app, phase, e)
                if continue_sending is False:
                    self.info("App '%s' cancelled outgoing message", app.name)
                    return False

        # now send the message out
        message.connection.backend.send(message)
        self.debug("SENT message '%s' to %s via %s" % (message.text,\
			message.connection.identity, message.connection.backend.name))
        return True
