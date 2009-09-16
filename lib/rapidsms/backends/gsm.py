#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import pygsm

from rapidsms.connection import Connection
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.backends import Backend as BackendBase


# number of seconds to wait between
# polling the modem for incoming SMS
POLL_INTERVAL = 10


class Backend(BackendBase):
    _title = "pyGSM"


    def configure(self, **kwargs):

        # strip any config settings that
        # obviously aren't for the modem
        for arg in ["title", "name"]:
            if arg in kwargs:
                kwargs.pop(arg)

        # store the rest to pass on to the
        # GsmModem() when RapidSMS starts
        self.modem_kwargs = kwargs
        self.modem = None


    def send(self, message):
        self.sent_messages += 1
        
        self.modem.send_sms(
            str(message.connection.identity),
            message.text)


    def gsm_log(self, modem, str, level):
        self.debug("%s: %s" % (level, str))


    def status(self):
        csq = self.modem.signal_strength()

        # convert the "real" signal
        # strength into a 0-4 scale
        if   not csq:   level = 0
        elif csq >= 30: level = 4
        elif csq >= 20: level = 3
        elif csq >= 10: level = 2
        else:           level = 1

        vars = {
            "_signal":  level,
            "_title":   self.title,
            "Messages Sent": self.sent_messages,
            "Messages Received": self.received_messages }

        # pygsm can return the name of the network
        # operator since b19cf3. add it if we can
        if hasattr(self.modem, "network"):
            vars["Network Operator"] = self.modem.network

        return vars


    def run(self):
        while self.running:
            self.info("Polling modem for messages")
            msg = self.modem.next_message()

            if msg is not None:
                self.received_messages += 1

                # we got an sms! hand it off to the
                # router to be dispatched to the apps
                x = self.message(msg.sender, msg.text)
                self.router.send(x)

            # wait for POLL_INTERVAL seconds before continuing
            # (in a slightly bizarre way, to ensure that we abort
            # as soon as possible when the backend is asked to stop)
            for n in range(0, POLL_INTERVAL):
                if not self.running: return None
                time.sleep(1)


    def start(self):
        self.sent_messages = 0
        self.received_messages = 0

        self.modem = pygsm.GsmModem(
            logger=self.gsm_log,
            **self.modem_kwargs)

        # If we connected successfully to the modem, call
        # superclass to start the run loop -- it just sets
        # self._running to True and calls run.
        if self.modem is not None:
            BackendBase.start(self)


    def stop(self):
        
        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        BackendBase.stop(self)

        # disconnect from modem
        if self.modem is not None:
            self.modem.disconnect()
