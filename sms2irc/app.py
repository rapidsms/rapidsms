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
            if message.connection.backend is not self.irc_backend:
                self.forward(message)
        else:
            self.error('Oops! sms2irc cannot find an irc backend to forward to')

    def outgoing(self, message):
        if self.irc_backend is not None:
            if message.connection.backend is not self.irc_backend:
                self.forward(message)
        else:
            self.error('Oops! sms2irc cannot find an irc backend to forward to')
        
    def forward(self, message):
        self.info("%s(%s): '%s' forwarded to %s" % (message.connection.identity, message.connection.backend.name, message.text, self.irc_backend.channels))
        txt = "(%s) says '%s'" % (message.connection.backend.name, message.text)
        Message(self.irc_backend, message.connection.identity, txt).send()
