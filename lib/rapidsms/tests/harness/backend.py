from rapidsms.backends.base import BackendBase


outbox = []


class MockBackend(BackendBase):
    """
    A simple mock backend, modeled after the BucketBackend
    """

    def __init__(self, *args, **kwargs):
        super(MockBackend, self).__init__(*args, **kwargs)
        self.messages = []

    def send(self, msg):
        self.messages.append(msg)
        outbox.append(msg)
        return True

    def next_outgoing_message(self):
        try:
            outbox.pop(0)
        except IndexError:
            return None
