#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App(rapidsms.app.App):
    def start(self):
        raise NotImplementedError
    
    def parse(self, msg):
        raise NotImplementedError
    
    def handle(self, msg):
        raise Exception("I'm not touching this one!")

    def cleanup(self, msg):
        raise NotImplementedError
