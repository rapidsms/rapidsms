#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
from django.conf import settings
from rapidsms.backends.base import BackendBase
from rapidsms.messages import IncomingMessage, OutgoingMessage
import rapidsms


class App(rapidsms.App):
    """
    What
    
    Settings::
    MESSAGE_TESTER_TIMEOUT (4)
    MESSAGE_TESTER_INTERVAL (0.25)
    """


    def _wait_for_message(self, msg):
        countdown = getattr(settings, "MESSAGE_TESTER_TIMEOUT", 4)
        interval  = getattr(settings, "MESSAGE_TESTER_INTERVAL", 0.25)

        while countdown > 0:
            if msg.processed:
                break

            # messages are usually processed before the first interval,
            # but pause a (very) short time before checking again, to
            # avoid pegging the cpu.
            countdown -= interval
            time.sleep(interval)


    def start(self):
        try:
            self.backend

        except KeyError:
            raise KeyError(
                "To use the message tester app, you must add a bucket " +\
                "backend named 'message_tester' to your INSTALLED_BACKENDS")


    @property
    def backend(self):
        return self.router.backends["message_tester"]


    def ajax_POST_send(self, get, post):
        msg = self.backend.receive(
            post.get("identity", None),
            post.get("text", ""))

        self._wait_for_message(msg)
        return True


    def ajax_GET_log(self, get):
        def _direction(msg):
            if isinstance(msg, OutgoingMessage): return "out"
            if isinstance(msg, IncomingMessage): return "in"
            return None

        def _json(msg):
            return {
                "identity": msg.connection.identity,
                "direction": _direction(msg),
                "text": msg.text }

        return map(_json, self.backend.bucket)
