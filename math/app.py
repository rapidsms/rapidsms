#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import random

class App(rapidsms.app.App):
    def start(self):
        self.questions = {}
        
    def __rand(self):
        return random.randrange(1, 99)
    
    def handle(self, msg):
    
        if not msg.caller in self.questions:
            a = self.__rand()
            b = self.__rand()
            self.questions[msg.caller] = [a, b]
            msg.respond("What's %d + %d?" % (a, b))
            
        # if we are waiting for an
        # answer, check it and respond
        else:
            a, b = self.questions[msg.caller]
            del(self.questions[msg.caller])
            if (a + b) == (int(msg.text)): msg.respond("Correct!")
            else: msg.respond("Wrong! It's %d" % (a + b))
