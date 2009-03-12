#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
from rapidsms.message import Message

# a pointless app to demonstrate the structure
# of sms applications without magic decorators
class App(rapidsms.app.App):

    def start(self):
        self.name = 'sms2irc'
        self.irc_backend = None
        for backend in self.router.backends:
            if backend._name == 'irc':
                self.irc_backend = backend
                  
    def parse(self, message):
        pass
            
    def handle(self, message):
        if self.irc_backend is not None:
            self.forward(message)

    def outgoing(self, message):
        if self.irc_backend is not None:
            if message.backend is not self.irc_backend:
                self.forward(message)
        
    def forward(self, message):
        self.info("%s(%s): '%s' forwarded to %s" % (message.caller, message.backend.name, message.text, self.irc_backend.channels))
        txt = "(%s) says '%s'" % (message.backend.name, message.text)
        Message(self.irc_backend, message.caller, txt).send()
