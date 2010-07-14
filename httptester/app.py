#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
from rapidsms.conf import settings
from rapidsms.apps.base import AppBase
from rapidsms.backends.base import BackendBase
from rapidsms.messages import IncomingMessage, OutgoingMessage


class App(AppBase):
    """
    What
    """


    def _wait_for_message(self, msg):
        countdown = settings.MESSAGE_TESTER_TIMEOUT
        interval  = settings.MESSAGE_TESTER_INTERVAL

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
            self.info(
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
