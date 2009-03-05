#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms.component

class Backend(rapidsms.component.Component):
    def __init__ (self, router):
        self.router = router
        self.running = False

    def start(self):
        self.running = True
        try:
            self.run()
        finally:
            self.running = False

    def run (self):
        raise NotImplementedError
    
    def stop(self):
        self.running = False
    
    def send(self):
        raise NotImplementedError
    
    def receive(self):
        raise NotImplementedError
