#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Backend(object):
    def __init__ (self, router):
        self.router = router
    
    def log(self, level, message):
        self.router.log(level, message)

    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    def send(self):
        raise NotImplementedError
    
    def receive(self):
        raise NotImplementedError
