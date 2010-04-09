#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import datetime
import rapidsms
from .models import Message


class App(rapidsms.App):
    def _who(self, msg):
        if   msg.contact:    return { "contact":    msg.contact }
        elif msg.connection: return { "connection": msg.connection }
        raise ValueError

    def _log(self, direction, who, text):
        return Message.objects.create(
            date=datetime.datetime.now(),
            direction=direction,
            text=text,
            **who)

    def parse(self, msg):    self._log("I", self._who(msg), msg.raw_text)
    def outgoing(self, msg): self._log("O", self._who(msg), msg.text)
