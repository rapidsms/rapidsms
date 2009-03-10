#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import ConfigParser


def to_list (item):
    return filter(None,map(lambda x: unicode(x).strip(), item.split(",")))

class Config (object):
    def __init__(self, *paths):
        self.parser = ConfigParser.ConfigParser()
        self.data   = {}
        self.parser.read(paths)
        for section in map(unicode, self.parser.sections()):
            data = {}
            for option in self.parser.options(section):
                data[option] = self.parser.get(section, option)
            
            # if this class has a parser specifically for this
            # named section, call it and replace the raw contents
            # (which are already in data[section]) with the result
            section_parser = "parse_%s_section" % (section)
            if hasattr(self, section_parser):
                data = getattr(self, section_parser)(data)
            
            self.data[section] = data

    def parse_rapidsms_section (self, data):
        app_classes = to_list(data["apps"])
        backend_classes = to_list(data["backends"])
        return { "apps": app_classes,
                 "backends": backend_classes }

    def __getitem__(self, key):
        return self.data[key]
        
    def has_key(self, key):
        return self.data.has_key(key)
