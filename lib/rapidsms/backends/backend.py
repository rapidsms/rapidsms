#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import component

class Backend(object, component.Component):
    
    def __init__ (self, router):
        self.router = router
        self.running = False
        
    def _get_name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return unicode(type(self))   

    def _set_name(self, name):
        self._name = name

    name = property(_get_name, _set_name)

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
