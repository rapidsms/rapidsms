#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import ConfigParser
import log


def to_list (item):
    return filter(None,map(lambda x: unicode(x).strip(), item.split(",")))

class Config (object):
    def __init__(self, *paths):
        self.parser = ConfigParser.ConfigParser()
        self.data   = {}
        self.parser.read(paths)
        sections = map(unicode, self.parser.sections())
        
        # pass 1 - get the raw data
        for section in sections:
            data = {}
            for option in self.parser.options(section):
                data[option] = self.parser.get(section, option)
            self.data[section] = data

        # pass 2 - parse the specific sections
        for section in sections:
            # if this class has a parser specifically for this
            # named section, call it and replace the raw contents
            # (which are already in data[section]) with the result
            section_parser = "parse_%s_section" % (section)
            if hasattr(self, section_parser):
                self.data[section] = \
                    getattr(self, section_parser)(self.data, self.data[section])

    def get_component_config(self, title, data):
        component = data.get(title, {}).copy() # defaults to empty config
        component["title"] = title
        if not "type" in component:
            component["type"] = title
        return component

    def parse_rapidsms_section (self, data, section):
        app_titles     = to_list(section["apps"])
        backend_titles = to_list(section["backends"])
        apps     = [self.get_component_config(app_title, data) for app_title in app_titles]
        backends = [self.get_component_config(backend_title, data) for backend_title in backend_titles]
        return { "apps": apps,
                 "backends": backends }

    def parse_log_section(self, data, section):
        output = {"level": log.LOG_LEVEL, "file": log.LOG_FILE}
        output.update(section)
        return output

    def __getitem__(self, key):
        return self.data[key]
        
    def has_key(self, key):
        return self.data.has_key(key)

    __contains__ = has_key
