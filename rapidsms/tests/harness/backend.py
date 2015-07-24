from rapidsms.backends.base import BackendBase
from rapidsms.errors import MessageSendingError


class MockBackend(BackendBase):
    """Simple backend that stores sent messages."""

    def __init__(self, *args, **kwargs):
        super(MockBackend, self).__init__(*args, **kwargs)
        self.messages = []

    def clear(self):
        del self.messages[:]

    def send(self, **kwargs):
        self.messages.append(kwargs)
        return True


class RaisesBackend(BackendBase):
    """Backend that always raises an error."""

    def send(self, **kwargs):
        raise Exception('Error!')


class FailedIdentitiesBackend(BackendBase):
    """Backend that fails if there's a 1 in the identity."""

    def send(self, id_, text, identities, context=None):
        failures = [identity for identity in identities if '1' in identity]
        if failures:
            raise MessageSendingError(failed_identities=failures)
