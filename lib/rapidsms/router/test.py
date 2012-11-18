"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


apps = None
inbound = []
outbound = []
disable_phases = False


def reset_state():
    """Clear inbound and outbound values."""
    global disable_phases, apps
    apps = None
    disable_phases = False
    del inbound[:]
    del outbound[:]


class TestRouter(BlockingRouter):
    """BlockingRouter that doesn't load apps and backends by default."""

    def __init__(self, *args, **kwargs):
        """
        Allow apps and backends to be customized, otherwise leave empty
        """
        if apps is not None:
            kwargs['apps'] = kwargs.get('apps', apps)
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
