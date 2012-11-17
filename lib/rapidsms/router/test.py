"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


inbound = []
outbound = []


def clear():
    """Clear inbound and outbound values."""
    del inbound[:]
    del outbound[:]


class TestRouter(BlockingRouter):
    """BlockingRouter that doesn't load apps and backends by default."""

    def __init__(self, *args, **kwargs):
        """
        Allow apps and backends to be customized, otherwise leave empty
        """
        kwargs['apps'] = kwargs.get('apps', [])
        kwargs['backends'] = kwargs.get('backends', {})
        super(TestRouter, self).__init__(*args, **kwargs)
        clear()

    def receive_incoming(self, msg):
        """Save all inbound messages locally for test inspection"""
        inbound.append(msg)
        super(TestRouter, self).receive_incoming(msg)

    def send_outgoing(self, msg):
        """Save all outbound messages locally for test inspection"""
        outbound.append(msg)
        super(TestRouter, self).send_outgoing(msg)


class NoOpTestRouter(TestRouter):
    """
    BlockingRouter that short circuits incoming and outgoing messages before
    passing them to the backend.  This should only be used for testing the
    Django view side of backend apps.
    """

    def receive_incoming(self, msg):
        if not hasattr(self, '_incoming'):
            self._incoming = []
        self._incoming.append(msg)

    def send_outgoing(self, msg):
        if not hasattr(self, '_outgoing'):
            self._outgoing = []
        self._outgoing.append(msg)
