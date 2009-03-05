#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import component

class App(component.Component):
    
    def __init__(self, router):
        self.router = router
            
    def _get_name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return unicode(type(self))   
            
    def _set_name(self, name):
        self._name = name
            
    name = property(_get_name, _set_name)

    def start (self):
        pass

    def parse (self, message):
        pass

    def handle (self, message):
        pass

    def cleanup (self, message):
        pass

    def outgoing (self, message):
        pass

    def stop (self):
        pass
