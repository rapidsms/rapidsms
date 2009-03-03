#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import models
from models import OutgoingMessage, IncomingMessage

class App(rapidsms.app.Base):

    def incoming(self, message):
        msg = IncomingMessage(caller=message.caller, text=message.text, 
            received=message.received)
        msg.save()
    
    def outgoing(self, message):
        msg = OutgoingMessage(caller=message.caller, text=message.text, 
            sent=message.sent)
        msg.save()
