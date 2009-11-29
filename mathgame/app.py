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
    
        if not msg.connection.identity in self.questions:
            a = self.__rand()
            b = self.__rand()
            self.questions[msg.connection.identity] = [a, b]
            msg.respond("What's %d + %d?" % (a, b))
	    return True
            
        # if we are waiting for an
        # answer, check it and respond
        else:
            a, b = self.questions[msg.connection.identity]
            del(self.questions[msg.connection.identity])
            if (a + b) == (int(msg.text)): msg.respond("Correct!")
            else: 
	        msg.respond("Wrong! It's %d" % (a + b))
		return True
