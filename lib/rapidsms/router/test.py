"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


inbound = []
outbound = []
disable_phases = True


def reset_router():
    """Clear inbound and outbound values."""
    global disable_phases
    disable_phases = True
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

    def receive_incoming(self, msg):
        """Save all inbound messages locally for test inspection"""
        inbound.append(msg)
        # short-circut router phases if disabled
        if disable_phases:
            return
        super(TestRouter, self).receive_incoming(msg)

    def send_outgoing(self, msg):
        """Save all outbound messages locally for test inspection"""
        outbound.append(msg)
        # short-circut router phases if disabled
        if disable_phases:
            return
        super(TestRouter, self).send_outgoing(msg)
