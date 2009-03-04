#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

# another pointless app
class App(rapidsms.app.App):

    def incoming(self, message):
        message.respond("Beta!")
