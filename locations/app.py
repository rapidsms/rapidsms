#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import rapidsms
from models import *


class App(rapidsms.app.App):
    PATTERN = re.compile(r"^(.+)\b(?:at)\b(.+?)$")
    
    def __find_location(self, text):
        try:
            # check for a location code first
            return Location.objects.get(code__iexact=text)

        # nothing else is supported, for now!
        except Location.DoesNotExist:
            return None

    def parse(self, msg):
        
        # if this message ends in "at SOMEWHERE",
        # we have work to do. otherwise, ignore it
        m = self.PATTERN.match(msg.text)
        if m is not None:
            
            # resolve the string into a Location object
            # (or None), and attach it to msg for other
            # apps to deal with
            text = m.group(2).strip()
            msg.location = self.__find_location(text)
            
            # strip the location tag from the message,
            # so other apps don't have to deal with it
            msg.text = m.group(1)
            
            # we should probably log this crazy behavior...
            self.info("Stripped Location code: %s" % text)
            self.info("Message is now: %s" % msg.text)
