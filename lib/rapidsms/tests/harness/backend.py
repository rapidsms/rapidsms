from rapidsms.backends.base import BackendBase


class MockBackend(BackendBase):
    """Simple backend that stores sent messages."""

    def __init__(self, *args, **kwargs):
        super(MockBackend, self).__init__(*args, **kwargs)
        self.messages = []

    def clear(self):
        del self.messages[:]

    def send(self, msg):
        self.messages.append(msg)
        return True
