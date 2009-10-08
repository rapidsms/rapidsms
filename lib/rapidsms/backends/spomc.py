#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re, time
import spomsky
from rapidsms.backends.base import BackendBase


class Backend(BackendBase):
    _title = "SPOMC"


    def configure(self, host="localhost", port=8100, **kwargs):
        self.client = spomsky.Client(host, port)


    def status(self):
        return {
            "_signal": None,
            "_title": self.title
        }


    def __callback(self, source, message_text):
        # drop the "sms://" protocol from the source
        phone_number = re.compile("[a-z]+://").sub("", source)

        # pass it off to the router for dispatch
        x = self.message(phone_number, message_text)
        self.router.incoming_message(x)


    def send(self, message):
        destination = "%s" % (message.connection.identity)
        sent = self.client.send(destination, message.text)


    def start(self):
        self.client.subscribe(self.__callback)
        BackendBase.start(self)


    def stop(self):
        BackendBase.stop(self)
        self.client.unsubscribe()
