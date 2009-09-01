#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import rapidsms
from apps.reporters.models import PersistantConnection
from models import OutgoingMessage, IncomingMessage


class App(rapidsms.App):
    def _who(self, msg):
        return PersistantConnection.from_message(msg).dict

    def handle(self, msg):
        IncomingMessage.objects.create(
            text=msg.text, **self._who(msg))

    def outgoing(self, msg):
        OutgoingMessage.objects.create(
            text=msg.text, **self._who(msg))
