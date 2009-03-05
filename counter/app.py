#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App(rapidsms.app.App):
    
    def start(self):
        self.counters = {}
    
    def parse(self, msg):
        if not hasattr(self.counters, msg.caller):
            self.counters[msg.caller] = 0
    
    def handle(self, msg):
        self.counters[msg.caller] += 1
        msg.respond("You've spoken to me %d times!" % (self.counters[msg.caller]))
