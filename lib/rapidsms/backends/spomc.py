#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from backend import Backend
from rapidsms.message import Message

import spomsky
import re


class Spomc(Backend):
    
    def __init__(self, router, host="localhost", port=8100):
        Backend.__init__(self,router)
        self.client = spomsky.Client(host, port)
    
    def __callback(self, source, message_text):
        
        # drop the "sms://" protocol from the source
        phone_number = re.compile("[a-z]+://").sub("", source)
        
        # create a message object, and
        # pass it off to the router
        m = Message(self, phone_number, message_text)
        self.router.send(m)

    def send(self, message):
        destination = "sms://%s" % (message.caller)
        self.client.send(destination, message.text)
        
    def start(self):
        self.client.subscribe(self.__callback)

    def stop(self):
        self.client.unsubscribe()
