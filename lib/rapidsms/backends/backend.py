#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.component import Receiver

class Backend (Receiver):
    def __init__ (self, router):
        super(Receiver, self).__init__()
        self._router = router
        self.running = False
        super(Receiver,self).__init__()
       
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
   
    def receive(self, caller, text):
        # turn the caller/text into a message object
        msg = Message(self, caller, text)
        # and send it off to the router
        self._router.incoming(msg)
