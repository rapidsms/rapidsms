#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import models
from models import OutgoingMessage, IncomingMessage

class App(rapidsms.app.App):
    # save messages on 'parse' so that 
    # annotations can be added to persistent message object by other apps
    def parse(self, msg):
        # make and save messages on their way in and 
        # cast connection as string so pysqlite doesnt complain
        persistent_msg = IncomingMessage.objects.create(identity=msg.connection.identity, text=msg.text,
            backend=msg.connection.backend.slug)
        msg.persistent_msg = persistent_msg
        self.debug(persistent_msg)
    
    def outgoing(self, message):
        # make and save messages on their way out and 
        # cast connection as string so pysqlite doesnt complain
        msg = OutgoingMessage.objects.create(identity=message.connection.identity, text=message.text, 
                                             backend=message.connection.backend.slug)
        self.debug(msg)
        # inject this id into the message object.
        message.logger_id = msg.id;
