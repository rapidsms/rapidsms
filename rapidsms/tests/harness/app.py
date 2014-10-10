from rapidsms.apps.base import AppBase


class MockApp(AppBase):
    """A subclass of AppBase with all the moving parts replaced."""

    def __init__(self, *args, **kwargs):
        super(MockApp, self).__init__(*args, **kwargs)
        self.calls = []
        self.return_values = {}

    def start(self):
        self.calls.append("start")
        return self.return_values.get('start', None)

    def filter(self, message):
        self.calls.append("filter")
        return self.return_values.get('filter', None)

    def parse(self, message):
        self.calls.append("parse")
        return self.return_values.get('parse', None)

    def handle(self, message):
        self.calls.append("handle")
        return self.return_values.get('handle', None)

    def default(self, message):
        self.calls.append("default")
        return self.return_values.get('default', None)

    def cleanup(self, message):
        self.calls.append("cleanup")
        return self.return_values.get('cleanup', None)

    def outgoing(self, message):
        self.calls.append("outgoing")
        return self.return_values.get('outgoing', None)

    def stop(self):
        self.calls.append("stop")
        return self.return_values.get('stop', None)


class EchoApp(MockApp):
    """Barebones echo app."""

    def handle(self, message):
        MockApp.handle(self, message)
        peer = message.connections[0].identity
        message.respond(peer + ": " + message.text)
