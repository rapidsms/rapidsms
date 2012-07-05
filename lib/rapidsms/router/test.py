"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


class TestRouter(BlockingRouter):
    """ BlockingRouter that doesn't load apps and backends by default """

    def __init__(self, *args, **kwargs):
        """
        Allow apps and backends to be customized, otherwise leave empty
        """
        kwargs['apps'] = kwargs.get('apps', [])
        kwargs['backends'] = kwargs.get('backends', {})
        super(TestRouter, self).__init__(*args, **kwargs)


class NoOpTestRouter(TestRouter):
    """
    BlockingRouter that short circuits incoming and outgoing messages before
    passing them to the backend.  This should only be used for testing the
    Django view side of backend apps.
    """

    def incoming(self, msg):
        if not hasattr(self, '_incoming'):
            self._incoming = []
        self._incoming.append(msg)

    def outgoing(self, msg):
        if not hasattr(self, '_outgoing'):
            self._outgoing = []
        self._outgoing.append(msg)

