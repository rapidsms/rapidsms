#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os

from rapidsms.router import Router
from rapidsms.backends.backend import Backend
from rapidsms.app import App


# a really dumb Logger stand-in
class MockLogger (list):
    def __init__(self):

	# enable logging during tests with an
	# environment variable, since the runner
	# doesn't seem to have args
	self.to_console = os.environ.get("verbose", False)

    def write (self, *args):
        if self.to_console:
            if len(args) == 3:
                print args[2]
            else:    
                print args[2] % args[3:]
        self.append(args)

# a subclass of Router with all the moving parts replaced
class MockRouter (Router):
    def __init__ (self):
        Router.__init__(self)
        self.logger = MockLogger()

    def add_backend (self, backend):
        self.backends.append(backend)

    def add_app (self, app):
        app.configure()
        self.apps.append(app)

    def start (self):
        self.running = True
        self.start_all_backends()
        self.start_all_apps()

    def stop (self):
        self.running = False
        self.stop_all_backends()

class MockBackend (Backend):
    def start (self):
        self._running = True
        self.outgoing = []

    def run (self):
        while self.running:
            msg = self.next_message(0.25)
            if msg is not None: self.outgoing.append(msg) 
 
# a subclass of App with all the moving parts replaced
class MockApp (App):
    def configure (self):
        self.calls = []

    def start (self):
        self.calls.append(("start",))

    def parse (self, message):
        self.calls.append(("parse", message))

    def handle (self, message):
        self.calls.append(("handle", message))

    def cleanup (self, message):
        self.calls.append(("cleanup", message))

    def outgoing (self, message):
        self.calls.append(("outgoing", message))

    def stop (self):
        self.calls.append(("stop",))

class EchoApp (MockApp):
    def handle (self, message):
        MockApp.handle(self, message)
        message.respond(message.peer + ": " + message.text)
