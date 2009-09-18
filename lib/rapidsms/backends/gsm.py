#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time
import pygsm

from rapidsms.connection import Connection
from rapidsms.messages.incoming import IncomingMessage
from rapidsms.backends import Backend as BackendBase


class Backend(BackendBase):
    _title = "pyGSM"

    # number of seconds to wait between
    # polling the modem for incoming SMS
    POLL_INTERVAL = 10

    # time to wait for the start method to
    # complete before assuming that it failed
    MAX_CONNECT_TIME = 10


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


    def __str__(self):
        return self._title


    def _wait_for_modem(self):
        """
        Blocks until this backend has connected to and initialized the modem,
        waiting for a maximum of self.MAX_CONNECT_TIME (default=10) seconds.
        Returns true when modem is ready, or false if it times out.
        """

        # if the modem isn't present yet, this message is probably being sent by
        # an application during startup from the main thread, before this thread
        # has connected to the modem. block for a short while before giving up.
        for n in range(0, self.MAX_CONNECT_TIME*10):
            if self.modem is not None: return True
            time.sleep(0.1)

        # timed out. we're still not connected
        # this is bad news, but not fatal, so warn
        self.warning("Timed out while waiting for modem")
        return False


    def send(self, message):

        # if this message is being sent from the start method of
        # an app (which is run in the main thread), this backend
        # may not have had time to start up yet. wait for it
        if not self._wait_for_modem():
            return False

        # attempt to send the message
        # failure is bad, but not fatal
        was_sent = self.modem.send_sms(
            str(message.connection.identity),
            message.text)

        if was_sent: self.sent_messages += 1
        else:        self.failed_messages += 1

        return was_sent


    def gsm_log(self, modem, str, level):
        self.debug("%s: %s" % (level, str))


    def status(self):

        # abort if the modem isn't connected
        # yet. there's no status to fetch
        if not self._wait_for_modem():
            return None

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
            for n in range(0, self.POLL_INTERVAL*10):
                if not self.running: return None
                time.sleep(0.1)


    def start(self):
        self.sent_messages = 0
        self.failed_messages = 0
        self.received_messages = 0

        self.modem = pygsm.GsmModem(
            logger=self.gsm_log,
            **self.modem_kwargs)

        # if we connected successfully to the modem, call
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
