from rapidsms.router import Router
from rapidsms.app import App

# a really dumb Logger stand-in
class MockLogger (list):
    def write (self, *args):
        self.append(args)

# a subclass of Router with all the moving parts replaced
class MockRouter (Router):
    def __init__ (self):
        Router.__init__(self)
        self.logger = MockLogger()

    def add_backend (self, backend):
        self.backends.append(backend)

    def add_app (self, app):
        self.apps.append(app)

    def start (self):
        self.running = True
        self.start_all_backends()
        self.start_all_apps()

    def stop (self):
        self.running = False
        self.stop_all_backends()

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
