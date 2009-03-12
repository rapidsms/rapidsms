#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
from rapidsms.message import Message

import spomsky
import re


class Backend(rapidsms.backends.Backend):
    
    def __init__(self, title, router, host="localhost", port=8100):
        rapidsms.backends.Backend.__init__(self, title, router)
        self.type="SPOMC"
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

    def stop(self):
        self.client.unsubscribe()
