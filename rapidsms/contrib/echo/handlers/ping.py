#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from rapidsms.contrib.handlers.handlers.base import BaseHandler


class PingHandler(BaseHandler):
    """
    Handle the (precise) message ``ping``, by responding with ``pong``.
    Useful for remotely checking that the router is alive.
    """

    @classmethod
    def dispatch(cls, router, msg):
        if msg.text == "ping":
            return msg.respond("pong")
