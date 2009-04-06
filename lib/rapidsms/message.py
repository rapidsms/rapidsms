#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import copy

from rapidsms.connection import Connection
from rapidsms.person import Person

class Message(object):
    def __init__(self, connection=None, text=None, person=None):
        if connection == None and person == None:
            raise Exception("Message __init__() must take one of: connection, person")
        self._connection = connection
        self.text = text
        self.person = person
        self.responses = []
    
    def __unicode__(self):
        return self.text

    @property
    def connection(self):
        # connection is read-only, since it's an
        # immutable property of this object
        if self._connection is not None:
            return self._connection
        else:
            return self.person.connection
    
    def send(self):
        """Send this message via self.connection.backend, returning
           True if the message was sent successfully."""
        return self.connection.backend.router.outgoing(self)

    def flush_responses (self):
        """Sends all responses added to this message (via the
           Message.respond method) in the order which they were
           added, and clears self.responses"""

        # keep on iterating until all of
        # the messages have been sent
        while self.responses:
            self.responses.pop(0).send()

    def respond(self, text):
        """Send the given text back to the original caller of this
           message on the same route that it came in on"""
        if self.connection:
            response = copy.copy(self)
            response.text = text
            self.responses.append(response)
            return True
        else: 
            return False
