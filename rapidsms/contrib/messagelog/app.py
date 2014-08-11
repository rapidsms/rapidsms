#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.utils import timezone
from rapidsms.apps.base import AppBase
from .models import Message


class MessageLogApp(AppBase):

    def _log(self, direction, msg):
        if not msg.connections:
            raise ValueError
        text = msg.raw_text if direction == Message.INCOMING else msg.text
        return Message.objects.create(
            date=timezone.now(),
            direction=direction,
            text=text,
            contact=msg.connections[0].contact,
            connection=msg.connections[0],
        )

    def parse(self, msg):
        # annotate the message as we log them in case any other apps
        # want a handle to them
        msg.logger_msg = self._log(Message.INCOMING, msg)

    def outgoing(self, msg):
        msg.logger_msg = self._log(Message.OUTGOING, msg)
