#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os, log
from ConfigParser import SafeConfigParser


def to_list (item, separator=","):
    return filter(None, map(lambda x: str(x).strip(), item.split(separator)))


class Config (object):
    def __init__ (self, *paths):
        self.parser = SafeConfigParser()
        
        # read the configuration, and store the list of
        # config files which were successfully parsed
        self.sources = self.parser.read(paths)
        
        self.raw_data = {}
        self.normalized_data = {}
        self.data = {}
        
        # first pass: read in the raw data. it's all strings, since
        # ConfigParser doesn't seem to decode unicode correctly (yet)
        for sn in self.parser.sections():
            items = self.parser.items(sn)
            self.raw_data[sn] = dict(items)
        
        # second pass: cast the values into int or bool where possible
        # (mostly to avoid storing "false", which evaluates to True)
        for sn in self.raw_data.keys():
            self.normalized_data[sn] = {}
            
            for key, val in self.raw_data[sn].items():
                self.normalized_data[sn][key] = \
                    self.__normalize_value(val)
        
        # third pass: iterate the normalized data, creating a
        # dict (self.data) containing the "real" configuration,
        # which may include things (magic, defaults, etc) not
        # present in the raw_data or normalized_data
        for sn in self.normalized_data.keys():
            section_parser = "parse_%s_section" % (sn)
            
            # if this section has a special parser, call
            # it with the raw data, and store the result
            if hasattr(self, section_parser):
                self.data[sn] = \
                    getattr(self, section_parser)(
                        self.normalized_data[sn])
            
            # no custom section parser, so
            # just copy the raw data as-is
            else:
                self.data[sn] =\
                    self.normalized_data[sn].copy()


    def __normalize_value (self, value):
        """Casts a string to a bool, int, or float, if it looks like it
           should be one. This is a band-aid over the ini format, which
           assumes all values to be strings. Examples:
           
           "mudkips"              => "mudkips" (str)
           "false", "FALSE", "no" => False     (bool)
           "true", "TRUE", "yes"  => True      (bool)
           "1.0", "0001.00"       => 1.0       (float)
           "0", "0000"            => 0         (int)"""
        
        # shortcut for string boolean values
        if   value.lower() in ["false", "no"]: return False
        elif value.lower() in ["true", "yes"]: return True
        
        # attempt to cast this value to an int, then a float. (a sloppy
        # benchmark of this exception-catching algorithm indicates that
        # it's faster than checking with a regexp)
        for func in [int, float]:
            try: func(value)
            except: pass
        
        # it's just a str
        # (NOT A UNICODE)
        return value
    
    
    def __import_class (self, class_tmpl):
        """Given a full class name (ie, apps.webui.app.App), returns the
           class object. There doesn't seem to be a built-in way of doing
           this without mucking with __import__."""
        
        # break the class name off the end of  module template
        # i.e. "apps.ABCD.app.App" -> ("apps.ABC.app", "App")
        try:
            module_str, class_str = class_tmpl.rsplit(".",1)
            module = __import__(module_str, {}, {}, [class_str])
            
            # import the requested class or None
            if hasattr(module, class_str):
                return getattr(module, class_str)
        
        except ImportError:
            pass


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
        
        return data

    
    def app_section (self, name):
        data = self.component_section(name)
        data["module"] = "apps.%s" % (data["type"])
        
        # load the config.py for this app, if possible
        config = self.__import_class("%s.config" % data["module"])
        if config is not None:
            
            # copy all of the names not starting with underscore (those are
            # private or __magic__) into this component's default config
            for var_name in dir(config):
                if not var_name.startswith("_"):
                    data[var_name] = getattr(config, var_name)
        
        # import the actual module, and add the path to the
        # config - it might not always be in rapidsms/apps/%s
        module_obj = self.__import_class(data["module"])
        if module_obj: data["path"] = module_obj.__path__[0]
        
        # return the component with the additional
        # app-specific data included.
        return data


    def backend_section (self, name):
        return self.component_section(name)
    
    
    def parse_rapidsms_section (self, raw_section):
        
        # "apps" and "backends" are strings of comma-separated
        # component names. first, break them into real lists
        app_names     = to_list(raw_section["apps"])
        backend_names = to_list(raw_section["backends"])
        
        # run lists of component names through component_section,
        # to transform into lists of dicts containing more meta-info
        return { "apps":     [self.app_section(n) for n in app_names],
                 "backends": [self.backend_section(n) for n in backend_names] }


    def parse_log_section (self, raw_section):
        output = {"level": log.LOG_LEVEL, "file": log.LOG_FILE}
        output.update(raw_section)
        return output


    def __getitem__ (self, key):
        return self.data[key]
        
    def has_key (self, key):
        return self.data.has_key(key)
    
    __contains__ = has_key
