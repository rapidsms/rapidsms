#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.component import Receiver
from rapidsms.message import Message

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
        raise NotImplementedError
    
    def stop(self):
        self._running = False
   
    def message(self, caller, text):
        return Message(self, caller, text)

    def route(self, msg):
        # send it off to the router
        self.router.send(msg)
