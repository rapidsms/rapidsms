#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.message import Message
import backend
import spomsky
import re

class Backend(backend.Backend):
    def configure(self, host="localhost", port=8100):
        self.client = spomsky.Client(host, port)
    
    def __callback(self, source, message_text):
        # drop the "sms://" protocol from the source
        phone_number = re.compile("[a-z]+://").sub("", source)
        
        # create a message object, and
        # pass it off to the router
        m = Message(self, phone_number, message_text)
        self.router.send(m)

    def send(self, message):
        destination = "%s" % (message.caller)
        self.client.send(destination, message.text)
        
    def start(self):
        self.client.subscribe(self.__callback)
        backend.Backend.start(self)

    def stop(self):
        backend.Backend.stop(self)
        self.client.unsubscribe()
        self.info("Shutting down...")
