#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms

class App(rapidsms.app.App):
    def handle(self, message):
        self.debug("got message %s" % (message))
        