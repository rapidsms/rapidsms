#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class Message(object):

    def __init__(self, backend, caller=None, text=None):
        self._backend = backend
        self.caller = caller
        self.text = text
        
        # initialize some empty attributes
        self.received = None
        self.sent = None
    
    def __unicode__(self):
        return self.text

    @property
    def backend(self):
        # backend is read-only, since it's an
        # immutable property of this object
        return self._backend
    
    def send(self):
        """Send this message via self.backend, returning
           True if the message was sent successfully."""
        return self._backend.router.outgoing(self)

    def respond(self, text):
        """Send the given text back to the original caller of this
           message on the same route that it came in on"""
        if self.caller: 
            return self.backend.router.outgoing(
                Message(self._backend, self.caller, text))
        else: 
            return False
