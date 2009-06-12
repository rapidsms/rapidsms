#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import pygsm

from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.backends import Backend
import backend

class Backend(Backend):
    _title = "pyGSM"
    
    
    def configure(self, *args, **kwargs):
        self.modem = None
        self.modem_args = args
        self.modem_kwargs = kwargs
    
    
    def send(self, message):
        self.modem.send_sms(
            str(message.connection.identity),
            message.text)
    
    
    def run(self):
        self.debug("GSM RUNNING: %s" % self._running)
        # check for new messages
        while self._running:
            msg = self.modem.next_message()
        
            if msg is not None:
                # we got an sms! create RapidSMS Connection and
                # Message objects, and hand it off to the router
                c = Connection(self, msg.sender)
                m = Message(c, msg.text)
                self.router.send(m)
                
            # poll for new messages
            # every two seconds
            time.sleep(2)
    
    
    def start(self):
        self.modem = pygsm.GsmModem(
            *self.modem_args,
            **self.modem_kwargs)

        if self.modem is not None:
            backend.Backend.start(self)

    def stop(self):
        if self.modem is not None:
            self.modem.disconnect()
        backend.Backend.stop(self)

        
