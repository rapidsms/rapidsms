#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import rapidsms
import re

class App(rapidsms.app.App):

    def configure(self, incoming='yes', outgoing='yes'):
        self._incoming = self.config_bool(incoming) 
        self._outgoing = self.config_bool(outgoing)

    def start(self):
        self.words = {}
        for line in open('apps/censor/censor.list', 'r').readlines():
            word = line.strip()
            self.words[word] = re.compile(r'%s' % word, re.I)

    def handle(self, msg):
        if self._incoming:
            self.debug("called handle!")
            if self.__find(msg.text):
                self.info("censored word found in incoming message... reprimanding caller!")
                msg.respond("Watch your mouth!")
                return True

    def outgoing(self, msg):
        if self._outgoing:
            self.debug("called outgoing!")
            if self.__find(msg.text):
                self.info("censored word found in outgoing message... cancelling send!")
                return False

    def __find(self, text):
        for word in self.words:
            self.debug("checking word '%s' in '%s'", word, text)
            if self.words[word].search(text):
                self.info("word '%s' found in message", word)
                return True
        return False
