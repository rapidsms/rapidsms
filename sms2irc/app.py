#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
from rapidsms.message import Message

# a pointless app to demonstrate the structure
# of sms applications without magic decorators
class App(rapidsms.app.App):
    def parse(self, message):
        # TODO move backend lookup into start() once load order is finalized
        self.backends = self.router.backends

        for backend in self.backends:
            print unicode(type(backend).__name__)
            if unicode(type(backend).__name__) == unicode('Irc'):
                self.irc_backend = backend
            
    def handle(self, message):
        self.forward(message)

    def outgoing(self, message):
        #self.forward(message)
        pass
        
    def forward(self, message):
        self.info("%s(%s): '%s' forwarded to %s" % (message.caller, message.backend.name, message.text, self.irc_backend.channels))
        txt = "(%s) says '%s'" % (message.backend.name, message.text)
        Message(self.irc_backend, message.caller, txt).send()
