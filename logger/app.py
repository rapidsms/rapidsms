#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

import models
from models import OutgoingMessage, IncomingMessage, MAX_LATIN_SMS_LEN

class App(rapidsms.app.App):
    # save messages on 'parse' so that 
    # annotations can be added to persistent message object by other apps
    def parse(self, msg):
        # make and save messages on their way in and 
        # cast connection as string so pysqlite doesnt complain
        text_to_save = msg.text
        if len(msg.text) > MAX_LATIN_SMS_LEN:
            text_to_save = msg.text[0:160]
        message = IncomingMessage.objects.create(identity=msg.connection.identity, text=text_to_save,
            backend=msg.connection.backend.slug)
        msg.persistent_msg = message
        self.debug(message)
    
    def outgoing(self, message):
        # make and save messages on their way out and 
        # cast connection as string so pysqlite doesnt complain
        msg = OutgoingMessage.objects.create(identity=message.connection.identity, text=message.text, 
                                             backend=message.connection.backend.slug)
        self.debug(msg.text)
        # inject this id into the message object.
        message.logger_id = msg.id;

