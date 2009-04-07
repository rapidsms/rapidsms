#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import re
import os

prefix      = re.compile(r'^fortune',re.I)
whitespace  = re.compile(r'\s+')

class App(rapidsms.app.App):
    def handle(self, message):
        self.debug("got message %s", message.text)
        if prefix.search(message.text):
            response = os.popen("fortune").read()
            if response:
                response = whitespace.sub(" ",response)
                self.debug("responding with %s", response)
                message.respond(response)
		return True
            else:
                self.warning("'fortune' program returned nothing")
