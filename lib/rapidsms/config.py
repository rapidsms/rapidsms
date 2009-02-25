#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from __future__ import with_statement
import simplejson

class Config():

    def __init__(self, path):
        # load the config, and parse it. i chose json because
        # it's in the python stdlib and is language-neutral
        f = open(path)
        self.raw = f.read()
        self.data = simplejson.loads(self.raw)

    def __getitem__(self, items):
        return self.data[items]
