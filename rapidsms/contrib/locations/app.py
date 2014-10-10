#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import re
import logging

from rapidsms.apps.base import AppBase

from .models import Location


logger = logging.getLogger(__name__)


class App(AppBase):
    PATTERN = re.compile(r"^(.+)\b(?:at)\b(.+?)$")

    def __find_location(self, text):
        try:
            # check for a location code first
            return Location.objects.get(slug__iexact=text)

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

            # split the text by space to find if it has a village
            # locCode,village = text.split()

            # location = self.__find_location(locCode)
            # location.village = village

            # msg.location = location
            msg.location = self.__find_location(text)

            # strip the location tag from the message,
            # so other apps don't have to deal with it
            msg.text = m.group(1)

            # we should probably log this crazy behavior...
            logger.info("Stripped Location code: %s" % text)
            logger.info("Message is now: %s" % msg.text)
