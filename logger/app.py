#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import models
from models import OutgoingMessage, IncomingMessage

class App(rapidsms.app.App):
    
    def handle(self, message):
        # make and save messages on their way in and 
        # cast backend as string so pysqlite doesnt complain
        msg = IncomingMessage(caller=message.caller, text=message.text,
            backend=str(message.backend), received=message.received)
        msg.save()
        self.debug(msg)
    
    def outgoing(self, message):
        # make and save messages on their way out and 
        # cast backend as string so pysqlite doesnt complain
        msg = OutgoingMessage(caller=message.caller, text=message.text, 
            backend=str(message.backend), sent=message.sent)
        msg.save()
        self.debug(msg)
