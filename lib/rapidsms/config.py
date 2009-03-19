#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from ConfigParser import SafeConfigParser
import log


def to_list (item, separator=","):
    return filter(None, map(lambda x: str(x).strip(), item.split(separator)))


class Config (object):
    def __init__ (self, *paths):
        self.parser = SafeConfigParser()
        self.parser.read(paths)
        
        self.raw_data = {}
        self.data = {}
        
        # first pass: read in the raw data. it's all strings, since
        # ConfigParser doesn't seem to decode unicode correctly (yet)
        for sn in self.parser.sections():
            items = self.parser.items(sn)
            self.raw_data[sn] = dict(items)

        # second pass: iterate the raw data, creating a second
        # dict (self.data) containing the "real" configuration,
        # which may include things (magic, defaults, etc) not
        # present in the raw_data
        for sn in self.raw_data.keys():
            section_parser = "parse_%s_section" % (sn)
            
            # if this section has a special parser, call
            # it with the raw data, and store the result
            if hasattr(self, section_parser):
                self.data[sn] = \
                    getattr(self, section_parser)(
                        self.raw_data[sn])
            
            # no custom section parser, so
            # just copy the raw data as-is
            else:
                self.data[sn] =\
                    self.raw_data[sn]


    def component_section (self, name):
        
        # fetch the current config for this section
        # from raw_data (or default to an empty dict),
        # then copy it, so we don't alter the original
        data = self.raw_data.get(name, {}).copy()
        
        # although "name" and "type" are deliberately distinct (to enable multiple
        # components of the same type to run concurrently), it's cumbersome to have
        # to provide a type every single time, so default to the name
        if not "type" in data:
            data["type"] = name
        
        try:
            # attempt to import the "config" module from the app's package, to
            # read in default configuration values. note that this DOES NOT
            # import the app, just it's config.py
            package_name = "apps.%s" % (data["type"])
            module = __import__(package_name, {}, {}, ["config"])
            if hasattr(module, "config"):
                
                # copy all of the names not starting with underscore (those are
                # private or __magic__) into this component's default config
                for var_name in dir(module.config):
                    if not var_name.startswith("_"):
                        data[var_name] = getattr(module.config, var_name)
        
        # no config module?
        # doesn't really matter
        except ImportError:
            pass
        
        # apps should set a title in their "config" module,
        # but in case they don't, recycle their name (again)
        if not "title" in data:
            data["title"] = name
        
        return data


    def parse_rapidsms_section (self, raw_section):
        
        # "apps" and "backends" are strings of comma-separated
        # component names. first, break them into real lists
        app_names     = to_list(raw_section["apps"])
        backend_names = to_list(raw_section["backends"])
        
        # run lists of component names through component_section,
        # to transform into lists of dicts containing more meta-info
        return { "apps":     [self.component_section(n) for n in app_names],
                 "backends": [self.component_section(n) for n in backend_names] }


    def parse_log_section (self, raw_section):
        output = {"level": log.LOG_LEVEL, "file": log.LOG_FILE}
        output.update(raw_section)
        return output


    def __getitem__ (self, key):
        return self.data[key]
        
    def has_key (self, key):
        return self.data.has_key(key)

    __contains__ = has_key
