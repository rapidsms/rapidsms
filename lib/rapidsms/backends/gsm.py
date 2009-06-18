#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import pygsm

from rapidsms.message import Message
from rapidsms.connection import Connection
from rapidsms.backends import Backend as BackendBase


# number of seconds to wait between
# polling the modem for incoming SMS
POLL_INTERVAL = 10


class Backend(BackendBase):
    _title = "pyGSM"


    def configure(self, *args, **kwargs):
        self.modem = None
        self.modem_args = args
        self.modem_kwargs = kwargs


    def send(self, message):
        self.modem.send_sms(
            str(message.connection.identity),
            message.text)


    def gsm_log(self, modem, str, level):
        self.debug("%s: %s" % (level, str))
    
    
    def run(self):
        while self.running:
            self.info("Polling modem for messages")
            msg = self.modem.next_message()
        
            if msg is not None:
                # we got an sms! create RapidSMS Connection and
                # Message objects, and hand it off to the router
                c = Connection(self, msg.sender)
                m = Message(c, msg.text)
                self.router.send(m)
            
            # wait for POLL_INTERVAL seconds before continuing
            # (in a slightly bizarre way, to ensure that we abort
            # as soon as possible when the backend is asked to stop)
            for n in range(0, POLL_INTERVAL):
                if not self.running: return None
                time.sleep(1)


    def start(self):
        self.modem = pygsm.GsmModem(
            logger=self.gsm_log,
            *self.modem_args,
            **self.modem_kwargs)
        
        # If we got the connection, call superclass to
        # start the run loop--it just sets self._running to True
        # and calls run.
        if self.modem is not None:
            BackendBase.start(self)


    def stop(self):
        
        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        BackendBase.stop(self)

        # disconnect from modem
        if self.modem is not None:
            self.modem.disconnect()
