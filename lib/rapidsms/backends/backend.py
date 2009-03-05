#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from rapidsms.component import Component, Receiver

class Backend (Component, Receiver):
    def __init__ (self, router):
        self._router = router
        self.running = False
       
    def _get_name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return unicode(type(self))   

    def _set_name(self, name):
        self._name = name

    name = property(_get_name, _set_name)

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
    

