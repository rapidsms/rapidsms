#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import time

from Queue import Queue, Empty

from ..models import Connection
from ..messages.incoming import IncomingMessage
from .base import BackendBase

from ..utils.modules import try_import
gammu = try_import('gammu')


class Backend(BackendBase):
    _title = "gammu"

    # number of seconds to wait between
    # polling the modem for incoming SMS
    POLL_INTERVAL = 1

    def configure(self, **kwargs):
        if gammu is None:
            raise ImportError(
                "The rapidsms.backends.gammu engine is not available, " +
                "because 'python-gammu' is not installed.")

        self.gammu_config = {'Connection': kwargs.get('connection', 'at'),
                             'Device': kwargs.get('device', '/dev/ttyUSB0')}

        self.sm = gammu.StateMachine()
        self.sm.SetConfig(0,self.gammu_config)
        self.outgoing_q = Queue()

    def __str__(self):
        return self._title

    def send(self, message):
        self.outgoing_q.put({'Text': message.text,
                             'SMSC': {'Location': 1},
                             'Number': message.connection.identity})
        return True

    def run(self):
        while self.running:
            try:
                self.sm.SendSMS(self.outgoing_q.get_nowait())
            except Empty:
                pass

            try:
                msg = self.sm.GetNextSMS(0, True)[0]
            except gammu.ERR_EMPTY:
                pass
            else:
                x = self.message(msg['Number'], msg['Text'])
                self.router.incoming_message(x)
                try:
                    self.sm.DeleteSMS(msg['Folder'], msg['Location'])
                except gammu.ERR_EMPTY:
                    pass
            
            for n in range(0, self.POLL_INTERVAL*10):
                if not self.running: return None
                time.sleep(0.1)

        self.info("Run loop terminated.")
        try:
            self.sm.terminate()
        except:
            pass


    def start(self):
        self.info("Connecting with gammu...")
        self.sm.Init()
            
        BackendBase.start(self)


    def stop(self):

        # call superclass to stop--sets self._running
        # to False so that the 'run' loop will exit cleanly.
        BackendBase.stop(self)

