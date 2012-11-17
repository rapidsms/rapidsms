#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import datetime
from rapidsms.apps.base import AppBase
from .models import Message


try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now


class App(AppBase):
    def _who(self, msg):
        to_return = {}
        if msg.contact:    to_return["contact"]    = msg.contact 
        if msg.connection: to_return["connection"] = msg.connection 
        if not to_return:
            raise ValueError
        return to_return

    def _log(self, direction, who, text):
        return Message.objects.create(
            date=datetime_now(),
            direction=direction,
            text=text,
            **who)

    def parse(self, msg):
        # annotate the message as we log them in case any other apps
        # want a handle to them
        msg.logger_msg = self._log("I", self._who(msg), msg.raw_text)

    def outgoing(self, msg): 
        msg.logger_msg = self._log("O", self._who(msg), msg.text)
