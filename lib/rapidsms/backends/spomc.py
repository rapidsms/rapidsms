#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.message import Message
from rapidsms.connection import Connection
import backend
import spomsky
import re, time

class Backend(backend.Backend):
    _title = "SPOMC"
    
    def configure(self, host="localhost", port=8100, **kwargs):
        self.client = spomsky.Client(host, port)
        
    def __callback(self, source, message_text):
        # drop the "sms://" protocol from the source
        phone_number = re.compile("[a-z]+://").sub("", source)
        
        # create connection and message objects, and
        # pass it off to the router
        c = Connection(self, phone_number)
        m = Message(c, message_text)
        self.router.send(m)

    def send(self, message):
        destination = "%s" % (message.connection.identity)
        sent = self.client.send(destination, message.text)
        
        # if the message wasn't sent, log it to the super
        # low-tech pending file, to be sent at some point
        # in the undefined future...
        if not sent:
        
            # TODO: move this to backend.py, and make it sane
            str = "%s:%s:%s" % (self.slug, destination, message.text)
            self.warning("DIDN'T SEND: %s" % (str))
            f = file("/tmp/rapidsms-pending", "a")
            f.write(str + "\n")
            f.close()
    
    def start(self):
        self.client.subscribe(self.__callback)
        backend.Backend.start(self)

    def stop(self):
        backend.Backend.stop(self)
        self.client.unsubscribe()
        self.info("Shutting down...")
