#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


class Config():

    def __init__(self, path):
        # load the config, and parse it. i chose json because
        # it's in the python stdlib and is language-neutral
        self.data = eval(file(path).read())

    def __getitem__(self, key):
        return self.data[key]
        
    def has_key(self, key):
        return self.data.has_key(key)
