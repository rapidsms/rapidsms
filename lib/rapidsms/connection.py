#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Connection(object):
    """The connection object pairs a backend with an individual
            identity (phone number, nickname, email, etc) so application
            authors need not concern themselves with backends."""
    def __init__(self, backend, identity):
        self.backend = backend
        # unique identity with respect to backend
        # (usually phone number, but may be a port number
        # or email address, etc)
        self.identity = identity

    def fork (self, identity):
        """Create a new connection on the same backend to a different
           identity."""
        return type(self)(self.backend, identity)
