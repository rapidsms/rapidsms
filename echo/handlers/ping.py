#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib.handlers.handlers.base import BaseHandler


class PingHandler(BaseHandler):
    """
    Handle the message ``ping``, by responding with ``Pong``. Useful for
    remotely checking that the router is alive.
    """

    def dispatch(self, router, msg):
        if msg.text.tolower() == "ping":
            self.respond("Pong")
