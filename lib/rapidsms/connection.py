#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import router 

class Connection(object):
    """The connection object pairs a backend with an individual
            identity (phone number, nickname, email, etc) so application
            authors need not concern themselves with backends."""
    def __init__(self, backend, identity):
        # Ok, connections should be able to find their backend even
        # for a name. 
        #
        # NOTE: The whole 'finding' a backend from a stored 'slug'
        # is _messed_ and probably shouldn't be here, but putting it
        # here for now at leasts encapsulates it in core where it 
        # should be instead of floating around everyone's app
        #
        if isinstance(backend,basestring):
            # try to find it from the router
            backend=router.get_router().get_backend(backend)

        if backend is None:
            raise Exception(\
                '%s is not a valid backend, did you add it to your rapidsms.ini?' % backend)
        
        self.backend = backend
        # unique identity with respect to backend
        # (usually phone number, but may be a port number
        # or email address, etc)
        self.identity = identity

    def fork (self, identity):
        """Create a new connection on the same backend to a different
           identity."""
        return type(self)(self.backend, identity)
