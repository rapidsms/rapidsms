#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Person(object):
    """The person object is a list of all of an individual's 
        connections (modalities of interacting with rapidsms), so
        applications can maintain individual identity across modalities."""
    def __init__(self):
        self.connections = []

    @property
    def connection(self):
        """Returns the first connection of this person by default"""
        return self.connections[0]

    def add_connection(self, connection):
        """Associate a new connection with this person, returning True
            if successful and False if this connnection is already known."""
        if connection not in self.connections:
            self.connections.append(connection)
            return True
        else:
            return False
