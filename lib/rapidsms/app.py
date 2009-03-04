#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

class Base (object):
    def start (self):
        pass

    def parse (self, message):
        pass

    def handle (self, message):
        pass

    def cleanup (self, message):
        pass

    def outgoing (self, message):
        pass

    def stop (self):
        pass
