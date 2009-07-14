#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from rapidsms.component import Receiver
from rapidsms.message import Message
from rapidsms.connection import Connection
import time

class Backend (Receiver):
    def __init__ (self, router):
        Receiver.__init__(self)
        self._router = router
        self._running = False
       
    @property
    def running (self):
        return self._running

    def start(self):
        self._running = True
        try:
            self.run()
        finally:
            self._running = False

    def run (self):
        while self.running:
            time.sleep(1)
    
    def stop(self):
        self._running = False
   
    def message(self, identity, text, date=None):
        c = Connection(self, identity)
        return Message(
            connection=c, 
            text=text, 
            date=date
            )

    def route(self, msg):
        # send it off to the router
        self.router.send(msg)
