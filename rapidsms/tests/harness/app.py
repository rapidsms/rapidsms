from rapidsms.apps.base import AppBase


class MockApp(AppBase):
    """A subclass of AppBase with all the moving parts replaced."""

    def __init__(self, *args, **kwargs):
        super(MockApp, self).__init__(*args, **kwargs)
        self.calls = []

    def start(self):
        self.calls.append(("start",))

    def parse(self, message):
        self.calls.append(("parse", message))

    def handle(self, message):
        self.calls.append(("handle", message))

    def cleanup(self, message):
        self.calls.append(("cleanup", message))

    def outgoing(self, message):
        self.calls.append(("outgoing", message))

    def stop(self):
        self.calls.append(("stop",))


class EchoApp(MockApp):
    """Barebones echo app."""

    def handle(self, message):
        MockApp.handle(self, message)
        message.respond(message.peer + ": " + message.text)
