"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


class TestRouter(BlockingRouter):
    """BlockingRouter that doesn't load apps and backends by default."""

    def __init__(self, *args, **kwargs):
        self.inbound = []
        self.outbound = []
        self.disable_phases = kwargs.pop('disable_phases', False)
        super(TestRouter, self).__init__(*args, **kwargs)

    def receive_incoming(self, msg):
        """Save all inbound messages locally for test inspection"""
        self.inbound.append(msg)
        # short-circut router phases if disabled
        if self.disable_phases:
            return
        super(TestRouter, self).receive_incoming(msg)

    def send_outgoing(self, msg):
        """Save all outbound messages locally for test inspection"""
        self.outbound.append(msg)
        # short-circut router phases if disabled
        if self.disable_phases:
            return
        super(TestRouter, self).send_outgoing(msg)
