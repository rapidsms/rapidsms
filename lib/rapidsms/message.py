#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import copy

class Message(object):
    def __init__(self, backend, caller=None, text=None):
        self._backend = backend
        self.caller = caller
        self.text = text
        self.responses = []
    
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
        return self.backend.router.outgoing(self)

    def flush_responses (self):
        for response in self.responses:
            response.send()
            self.responses.remove(response)

    def respond(self, text):
        """Send the given text back to the original caller of this
           message on the same route that it came in on"""
        if self.caller: 
            response = copy.copy(self)
            response.text = text
            self.responses.append(response)
            return True
        else: 
            return False
