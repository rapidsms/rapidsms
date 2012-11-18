from rapidsms.backends.base import BackendBase


outbox = []


def reset_state():
    del outbox[:]


class MockBackend(BackendBase):
    """Simple backend that stores sent messages to global variable"""

    def __init__(self, *args, **kwargs):
        super(MockBackend, self).__init__(*args, **kwargs)
        self.clear()

    def clear(self):
        self.messages = []
        reset_state()

    def send(self, msg):
        self.messages.append(msg)
        outbox.append(msg)
        return True

    def next_outgoing_message(self):
        try:
            outbox.pop(0)
        except IndexError:
            return None
